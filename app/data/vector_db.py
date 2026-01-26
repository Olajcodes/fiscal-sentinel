# RAG Logic (ChromaDB setup)

import os
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

# PATH CONFIGURATION
# This points to where you will drop your PDF files
DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db_store")

class LegalKnowledgeBase:
    def __init__(self):
        # Initialize ChromaDB (Persistent means it saves to disk, so you don't reload PDFs every run)
        self.client = chromadb.PersistentClient(path=DB_PATH)
        
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name="consumer_laws",
            embedding_function=self.embedding_fn
        )

    def ingest_documents(self):
        """
        Reads all PDFs in app/data/documents/ and stores them in the vector DB.
        Run this ONCE or whenever new laws are added.
        """
        if not os.path.exists(DOCS_DIR):
            os.makedirs(DOCS_DIR)
            print(f"Created directory {DOCS_DIR}. Please put PDF files there.")
            return

        print(f"📂 Scanning {DOCS_DIR} for PDFs...")
        
        files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf")]
        if not files:
            print("No PDFs found.")
            return

        for file_name in files:
            file_path = os.path.join(DOCS_DIR, file_name)
            print(f"📖 Processing {file_name}...")
            
            # Read PDF
            reader = PdfReader(file_path)
            text_chunks = []
            metadatas = []
            ids = []
            
            # Simple chunking by page
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    # Creating a unique ID for each chunk
                    chunk_id = f"{file_name}_page_{i}"
                    
                    text_chunks.append(text)
                    metadatas.append({"source": file_name, "page": i})
                    ids.append(chunk_id)
            
            # Add to Database
            if text_chunks:
                self.collection.upsert(
                    documents=text_chunks,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"✅ Indexed {len(text_chunks)} pages from {file_name}")

    def search_laws(self, query: str, n_results=2):
        """
        Retrieves the most relevant legal text for a given query from the DB.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Formatting the output for the LLM
        if not results["documents"][0]:
            return "No specific legal documents found."
            
        context = ""
        for i, doc in enumerate(results["documents"][0]):
            source = results["metadatas"][0][i]["source"]
            context += f"---\nSOURCE: {source}\nEXCERPT: {doc[:500]}\n---\n"
            
        return context

if __name__ == "__main__":
    kb = LegalKnowledgeBase()
    kb.ingest_documents()
