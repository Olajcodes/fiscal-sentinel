# RAG Logic (ChromaDB setup)

import os
import re
from html import unescape
from typing import Iterable, Optional

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

# PATH CONFIGURATION
DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db_store")


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


class LegalKnowledgeBase:
    def __init__(self):
        # Persistent means it saves to disk, so you don't reload PDFs every run.
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="consumer_laws",
            embedding_function=self.embedding_fn,
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

            if text_chunks:
                self.collection.upsert(documents=text_chunks, metadatas=metadatas, ids=ids)
                print(f"Indexed {len(text_chunks)} chunks from {file_name}")

    def search_laws(self, query: str, n_results: int = 2, merchant: Optional[str] = None):
        """
        Retrieves the most relevant legal text for a given query from the DB.
        If merchant is provided and present in metadata, retrieval is filtered.
        """
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
