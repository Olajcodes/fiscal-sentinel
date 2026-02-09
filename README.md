# Fiscal Sentinel

Fiscal Sentinel finds suspicious subscription charges in your bank statement and drafts dispute letters using verified policy evidence.

## What It Does
- Ingests bank statements (CSV or PDF), normalizes rows, and stores transactions.
- Answers transaction questions deterministically (highest charge, totals, by-merchant, date ranges).
- Retrieves legal and policy evidence only when the user asks about rights or requests a letter.
- Drafts dispute or cancellation letters only after explicit confirmation.

## Why It Matters
Consumers often do not know which charges are valid or how to contest them. Fiscal Sentinel makes the workflow fast, evidence-based, and safe by default.

## Product Flow (3 Minutes)
1. Upload a bank statement (PDF or CSV). Preview and confirm columns if needed and correct.
2. Ask a question like "Check out irregularities or supscious transaction in my account?"
3. Ask about legality or request a letter to trigger evidence-backed drafting.

## Key Features
- OCR + parsing pipeline with preview and column mapping confirmation.
- Deterministic transaction Q and A for common account questions.
- Strict retrieval gating to avoid irrelevant citations.
- Letter drafting with evidence excerpts when explicitly requested.
- Opik tracing for routing, retrieval use, and outcome quality.

## Tech Stack
- Backend: FastAPI + LangGraph
- Frontend: Streamlit (UI), deployable to Streamlit Cloud
- Embeddings: OpenAI (production) or SentenceTransformers (local)
- Vector DB: Qdrant (production) or Chroma (local)
- Tracing and evaluation: Opik

## Project Structure
```
fiscal-sentinel/
??? app/
?   ??? agent/          # LangGraph routing + prompts
?   ??? analysis/       # Transaction query + rules
?   ??? data/           # Documents + vector store + parsers
?   ??? evaluation/     # Opik metrics and experiments
??? frontend/           # Streamlit UI
??? main.py             # FastAPI backend
??? requirements.txt    # Production deps (Railway)
??? requirements.local.txt  # Local dev deps (Streamlit + Chroma + ST embeddings)
```

## Run Locally
1. Create and activate a virtual environment
```bash
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

2. Install local dependencies
```bash
pip install -r requirements.local.txt
```

3. Create a `.env` file
```
OPENAI_API_KEY=sk-...
OPIK_API_KEY=...
VECTOR_DB_PROVIDER=chroma
EMBEDDING_PROVIDER=local
DEFAULT_CURRENCY=NGN
DEFAULT_CURRENCY_SYMBOL=NGN
```

4. Run the backend
```bash
python main.py
```

5. Run the UI
```bash
streamlit run frontend/ui.py
```

## Production (Railway + Qdrant)
Recommended production settings use OpenAI embeddings + Qdrant.

Required Railway env vars:
```
OPENAI_API_KEY=...
OPIK_API_KEY=...
OPIK_WORKSPACE=olajcodes
OPIK_PROJECT_NAME=Fiscal Sentinel
VECTOR_DB_PROVIDER=qdrant
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIM=1536
QDRANT_URL=...
QDRANT_API_KEY=...
QDRANT_COLLECTION=consumer_laws
```

For OCR on Railway (PDF statements):
```
RAILPACK_DEPLOY_APT_PACKAGES=tesseract-ocr tesseract-ocr-eng poppler-utils
```

## Ingest RAG Documents
Add documents to `app/data/documents/` and ingest:
```bash
python -m app.data.vector_db
```

## API Overview
- `GET /` Health check
- `GET /transactions` List stored or mock transactions
- `POST /transactions/preview` Preview a CSV/PDF upload and get mapping suggestions
- `POST /transactions/confirm` Persist the previewed rows using a mapping
- `POST /transactions/upload` Direct upload without a preview step
- `POST /analyze` Ask the agent a question
- `GET /vector-db/health` Vector DB provider and count

## Streamlit Cloud
Set Streamlit secrets:
```
API_URL="https://fiscal-sentinel-production.up.railway.app"
```

## Evaluation (Opik)
Run the evaluation suite:
```bash
python run_experiment.py
```

Custom metrics live in `app/evaluation/metrics.py`:
- LegalCitationMetric
- ActionabilityMetric
- ConversationMetric
- RetrievalDisciplineMetric

## Demo Script (3 Minutes)
See `docs/demo_script.md`.

## Pitch Deck (10 Slides)
See `docs/pitch_deck.md`.


