# RAG Logic (ChromaDB setup)

import os
import re
from html import unescape
from typing import Iterable, Optional, List, Dict

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# PATH CONFIGURATION
DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db_store")
DEFAULT_COLLECTION = "consumer_laws"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

VECTOR_DB_PROVIDER = os.environ.get("VECTOR_DB_PROVIDER", "chroma").lower()
QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", DEFAULT_COLLECTION)


def _infer_metadata_from_filename(file_name: str):
    """
    Infer lightweight metadata from filenames so we can filter retrieval by merchant
    for the transaction dataset.
    """
    base = os.path.splitext(file_name)[0].lower()
    merchant = None
    doc_type = "unknown"

    if "netflix" in base:
        merchant, doc_type = "netflix", "terms"
    elif "planet" in base and "fitness" in base:
        merchant, doc_type = "planet_fitness", "terms"
    elif "adobe" in base:
        merchant, doc_type = "adobe", "terms"
    elif "spotify" in base:
        merchant, doc_type = "spotify", "terms"
    elif "amazon" in base:
        merchant, doc_type = "amazon", "terms"
    elif "ftc" in base:
        merchant, doc_type = "ftc", "regulation"
    elif "state" in base or "consumer" in base:
        merchant, doc_type = "generic", "regulation"

    return {"merchant": merchant, "document_type": doc_type}


def _is_pdf(file_path: str) -> bool:
    try:
        with open(file_path, "rb") as f:
            return f.read(5) == b"%PDF-"
    except Exception:
        return False


def _strip_html(raw_text: str) -> str:
    # Remove script/style blocks first.
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw_text)
    # Remove all remaining tags.
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)
    cleaned = unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> Iterable[str]:
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _clean_metadata(metadata: Dict[str, Optional[str]]) -> Dict[str, str]:
    return {k: v for k, v in metadata.items() if v is not None}


class LegalKnowledgeBase:
    def __init__(self):
        self.provider = VECTOR_DB_PROVIDER
        self.embedding_model = os.environ.get("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)

        if self.provider == "qdrant":
            if not QDRANT_URL:
                raise ValueError("QDRANT_URL is required when VECTOR_DB_PROVIDER=qdrant")
            self.qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
            self.embedder = SentenceTransformer(self.embedding_model)
            self.collection_name = QDRANT_COLLECTION
            self._ensure_qdrant_collection()
            self.collection = None
            self.client = None
            self.embedding_fn = None
        else:
            # Persistent means it saves to disk, so you don't reload PDFs every run.
            self.client = chromadb.PersistentClient(path=DB_PATH)
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model
            )
            self.collection = self.client.get_or_create_collection(
                name=DEFAULT_COLLECTION,
                embedding_function=self.embedding_fn,
            )
            self.qdrant = None
            self.embedder = None
            self.collection_name = DEFAULT_COLLECTION

    def _ensure_qdrant_collection(self) -> None:
        if self.qdrant.collection_exists(self.collection_name):
            return
        vector_size = self.embedder.get_sentence_embedding_dimension()
        self.qdrant.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance.COSINE,
            ),
        )

    def ingest_documents(self):
        """
        Reads all PDFs in app/data/documents/ and stores them in the vector DB.
        Run this ONCE or whenever new documents are added.
        """
        if not os.path.exists(DOCS_DIR):
            os.makedirs(DOCS_DIR)
            print(f"Created directory {DOCS_DIR}. Please put PDF files there.")
            return

        print(f"Scanning {DOCS_DIR} for PDFs...")

        files = [
            f
            for f in os.listdir(DOCS_DIR)
            if f.lower().endswith((".pdf", ".html", ".txt"))
        ]
        if not files:
            print("No PDFs found.")
            return

        for file_name in files:
            file_path = os.path.join(DOCS_DIR, file_name)
            print(f"Processing {file_name}...")

            text_chunks = []
            metadatas = []
            ids = []
            base_meta = _infer_metadata_from_filename(file_name)

            try:
                if _is_pdf(file_path):
                    reader = PdfReader(file_path)
                    # Simple chunking by page.
                    for i, page in enumerate(reader.pages):
                        text = page.extract_text()
                        if not text:
                            continue
                        chunk_id = f"{file_name}_page_{i}"
                        text_chunks.append(text)
                        metadatas.append({"source": file_name, "page": i, **base_meta})
                        ids.append(chunk_id)
                else:
                    with open(file_path, "rb") as f:
                        raw = f.read().decode("utf-8", errors="ignore")
                    text = _strip_html(raw)
                    for i, chunk in enumerate(_chunk_text(text)):
                        chunk_id = f"{file_name}_chunk_{i}"
                        text_chunks.append(chunk)
                        metadatas.append({"source": file_name, "page": i, **base_meta})
                        ids.append(chunk_id)
            except Exception as e:
                print(f"Skipping {file_name} due to error: {e}")
                continue

            if not text_chunks:
                continue

            if self.provider == "qdrant":
                payloads = []
                for meta, text in zip(metadatas, text_chunks):
                    payload = _clean_metadata(meta)
                    payload["text"] = text
                    payloads.append(payload)

                embeddings = self.embedder.encode(text_chunks, normalize_embeddings=True).tolist()
                points = [
                    qmodels.PointStruct(id=doc_id, vector=vector, payload=payload)
                    for doc_id, vector, payload in zip(ids, embeddings, payloads)
                ]
                self.qdrant.upsert(collection_name=self.collection_name, points=points)
                print(f"Indexed {len(text_chunks)} chunks from {file_name} into Qdrant")
            else:
                self.collection.upsert(documents=text_chunks, metadatas=metadatas, ids=ids)
                print(f"Indexed {len(text_chunks)} chunks from {file_name}")

    def search_laws(self, query: str, n_results: int = 2, merchant: Optional[str] = None):
        """
        Retrieves the most relevant legal text for a given query from the DB.
        If merchant is provided and present in metadata, retrieval is filtered.
        """
        if self.provider == "qdrant":
            query_vector = self.embedder.encode(query, normalize_embeddings=True).tolist()
            search_filter = None
            if merchant:
                search_filter = qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="merchant",
                            match=qmodels.MatchValue(value=merchant),
                        )
                    ]
                )
            results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=n_results,
                query_filter=search_filter,
            )
            if not results:
                return "No specific legal documents found."

            context = ""
            for hit in results:
                payload = hit.payload or {}
                doc = payload.get("text", "")
                source = payload.get("source", "unknown")
                page = payload.get("page", "?")
                merchant_meta = payload.get("merchant")
                context += (
                    "---\n"
                    f"SOURCE: {source}\n"
                    f"PAGE: {page}\n"
                    f"MERCHANT: {merchant_meta}\n"
                    f"EXCERPT: {doc[:500]}\n"
                    "---\n"
                )
            return context

        where = {"merchant": merchant} if merchant else None
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )

        if not results.get("documents") or not results["documents"][0]:
            return "No specific legal documents found."

        context = ""
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            source = meta.get("source", "unknown")
            page = meta.get("page", "?")
            merchant_meta = meta.get("merchant")
            context += (
                "---\n"
                f"SOURCE: {source}\n"
                f"PAGE: {page}\n"
                f"MERCHANT: {merchant_meta}\n"
                f"EXCERPT: {doc[:500]}\n"
                "---\n"
            )

        return context


if __name__ == "__main__":
    kb = LegalKnowledgeBase()
    kb.ingest_documents()
