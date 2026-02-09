# RAG Logic (ChromaDB setup)

import math
import os
import re
import uuid
from html import unescape
from typing import Iterable, Optional, List, Dict

from dotenv import load_dotenv
from pypdf import PdfReader
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# PATH CONFIGURATION
load_dotenv()
os.environ.setdefault("HF_HUB_READ_TIMEOUT", "60")
os.environ.setdefault("HF_HUB_CONNECT_TIMEOUT", "30")

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db_store")
DEFAULT_COLLECTION = "consumer_laws"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def _read_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.environ.get(name, default)
    if isinstance(value, str):
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1].strip()
    return value


VECTOR_DB_PROVIDER = (_read_env("VECTOR_DB_PROVIDER", "chroma") or "chroma").lower()
EMBEDDING_PROVIDER = (_read_env("EMBEDDING_PROVIDER", "local") or "local").lower()
OPENAI_EMBEDDING_MODEL = _read_env("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small"
OPENAI_EMBEDDING_DIM = int(_read_env("OPENAI_EMBEDDING_DIM", "1536") or "1536")
QDRANT_URL = _read_env("QDRANT_URL")
QDRANT_API_KEY = _read_env("QDRANT_API_KEY")
QDRANT_COLLECTION = _read_env("QDRANT_COLLECTION", DEFAULT_COLLECTION) or DEFAULT_COLLECTION
QDRANT_TIMEOUT_SECONDS = int(_read_env("QDRANT_TIMEOUT_SECONDS", "60") or "60")
EMBEDDING_BATCH_SIZE = int(_read_env("EMBEDDING_BATCH_SIZE", "32") or "32")
QDRANT_UPSERT_BATCH_SIZE = int(_read_env("QDRANT_UPSERT_BATCH_SIZE", "64") or "64")


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


def _to_point_id(raw_id: str) -> str:
    # Qdrant requires point IDs to be UUIDs or unsigned integers.
    return str(uuid.uuid5(uuid.NAMESPACE_URL, raw_id))


def _batch_items(items: List, batch_size: int) -> Iterable[List]:
    for idx in range(0, len(items), batch_size):
        yield items[idx : idx + batch_size]


def _load_sentence_transformer(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as exc:
        raise ImportError(
            "sentence-transformers is required when EMBEDDING_PROVIDER=local. "
            "Install it with `pip install -r requirements.local.txt`."
        ) from exc
    return SentenceTransformer(model_name)


def _load_chromadb():
    try:
        import chromadb
        from chromadb.utils import embedding_functions
    except Exception as exc:
        raise ImportError(
            "chromadb is required when VECTOR_DB_PROVIDER=chroma. "
            "Install it with `pip install -r requirements.local.txt`."
        ) from exc
    return chromadb, embedding_functions


def _l2_normalize(vectors: List[List[float]]) -> List[List[float]]:
    normalized = []
    for vec in vectors:
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        normalized.append([v / norm for v in vec])
    return normalized


class LegalKnowledgeBase:
    def __init__(self):
        self.provider = VECTOR_DB_PROVIDER
        self.embedding_provider = EMBEDDING_PROVIDER
        self.embedding_model = os.environ.get("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
        self.embedding_dim: Optional[int] = None
        self.openai_client: Optional[OpenAI] = None

        if self.provider == "qdrant":
            if not QDRANT_URL:
                raise ValueError("QDRANT_URL is required when VECTOR_DB_PROVIDER=qdrant")
            if self.embedding_provider == "openai":
                api_key = _read_env("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")
                self.embedding_model = _read_env("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL) or OPENAI_EMBEDDING_MODEL
                self.embedding_dim = int(_read_env("OPENAI_EMBEDDING_DIM", str(OPENAI_EMBEDDING_DIM)) or str(OPENAI_EMBEDDING_DIM))
                self.openai_client = OpenAI(api_key=api_key)
                self.embedder = None
            else:
                self.embedder = _load_sentence_transformer(self.embedding_model)
                self.embedding_dim = self.embedder.get_sentence_embedding_dimension()
            self.qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=QDRANT_TIMEOUT_SECONDS)
            self.collection_name = QDRANT_COLLECTION
            self._ensure_qdrant_collection()
            self.collection = None
            self.client = None
            self.embedding_fn = None
        else:
            # Persistent means it saves to disk, so you don't reload PDFs every run.
            chromadb, embedding_functions = _load_chromadb()
            self.client = chromadb.PersistentClient(path=DB_PATH)
            if self.embedding_provider == "openai":
                api_key = _read_env("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai")
                self.embedding_model = _read_env("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL) or OPENAI_EMBEDDING_MODEL
                if not hasattr(embedding_functions, "OpenAIEmbeddingFunction"):
                    raise ImportError("chromadb OpenAIEmbeddingFunction is unavailable in this version.")
                self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=api_key,
                    model_name=self.embedding_model,
                )
            else:
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
        vector_size = self.embedding_dim
        if vector_size is None and self.embedder is not None:
            vector_size = self.embedder.get_sentence_embedding_dimension()
        if vector_size is None:
            raise ValueError("Unable to determine embedding dimension for Qdrant collection.")
        self.qdrant.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance.COSINE,
            ),
        )

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        if self.embedding_provider == "openai":
            if not self.openai_client:
                self.openai_client = OpenAI()
            embeddings: List[List[float]] = []
            for batch in _batch_items(texts, EMBEDDING_BATCH_SIZE):
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=batch,
                )
                embeddings.extend([item.embedding for item in response.data])
            return _l2_normalize(embeddings)
        if not self.embedder:
            raise ValueError("Local embedder not initialized.")
        return self.embedder.encode(
            texts,
            normalize_embeddings=True,
            batch_size=EMBEDDING_BATCH_SIZE,
        ).tolist()

    def _embed_query(self, query: str) -> List[float]:
        return self._embed_texts([query])[0]

    def ingest_documents(self):
        """
        Reads all PDFs in app/data/documents/ and stores them in the vector DB.
        Run this ONCE or whenever new documents are added.
        """
        print(f"Vector DB provider: {self.provider} (collection={self.collection_name})")
        if not os.path.exists(DOCS_DIR):
            os.makedirs(DOCS_DIR)
            print(f"Created directory {DOCS_DIR}. Please put PDF files there.")
            return

        print(f"Scanning {DOCS_DIR} for PDFs...")
        total_chunks = 0

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

                embeddings = self._embed_texts(text_chunks)
                points = [
                    qmodels.PointStruct(id=_to_point_id(doc_id), vector=vector, payload=payload)
                    for doc_id, vector, payload in zip(ids, embeddings, payloads)
                ]
                for batch in _batch_items(points, QDRANT_UPSERT_BATCH_SIZE):
                    self.qdrant.upsert(collection_name=self.collection_name, points=batch)
                total_chunks += len(text_chunks)
                print(f"Indexed {len(text_chunks)} chunks from {file_name} into Qdrant")
            else:
                self.collection.upsert(documents=text_chunks, metadatas=metadatas, ids=ids)
                total_chunks += len(text_chunks)
                print(f"Indexed {len(text_chunks)} chunks from {file_name}")

        if total_chunks:
            print(f"Indexed {total_chunks} total chunks.")

    def search_laws(self, query: str, n_results: int = 2, merchant: Optional[str] = None):
        """
        Retrieves the most relevant legal text for a given query from the DB.
        If merchant is provided and present in metadata, retrieval is filtered.
        """
        if self.provider == "qdrant":
            query_vector = self._embed_query(query)
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

    def get_collection_stats(self) -> Dict[str, int]:
        """
        Returns total vector count for the active collection.
        """
        if self.provider == "qdrant":
            info = self.qdrant.get_collection(self.collection_name)
            vectors_count = getattr(info, "points_count", None)
            if vectors_count is None:
                vectors_count = getattr(info, "vectors_count", None)
            if vectors_count is None:
                try:
                    count_result = self.qdrant.count(collection_name=self.collection_name, exact=True)
                    vectors_count = getattr(count_result, "count", 0)
                except Exception:
                    vectors_count = 0
            return {"vectors_count": int(vectors_count or 0)}

        count = self.collection.count()
        return {"vectors_count": int(count)}


if __name__ == "__main__":
    kb = LegalKnowledgeBase()
    kb.ingest_documents()
