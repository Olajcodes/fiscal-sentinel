# Fiscal Sentinel

The AI financial assistant that helps users spot questionable charges and draft dispute or cancellation letters **only when requested**.

Fiscal Sentinel combines transaction analysis, retrieval-augmented generation (RAG) over consumer agreements/regulations, and a conversational UI with explicit confirmation before drafting letters.

## Key Behavior
- Conversational by default. Greetings and general questions do not trigger retrieval or letter drafting.
- Analysis first. When asked to scan transactions, the agent summarizes findings and asks before drafting a letter.
- Evidence only when needed. Legal citations are returned only if the user asks about legality, rights, or a letter.

## Tech Stack
- Frontend: Streamlit
- Backend: FastAPI
- Agent Orchestration: LangGraph
- Model: OpenAI (via API)
- Knowledge Base: ChromaDB + PyPDF (+ HTML/TXT parsing fallback)
- Evaluation/Tracing: Opik (Comet)
- Data: Mock Plaid transactions

## Project Structure
```
fiscal-sentinel/
├── app/
│   ├── agent/          # LangGraph routing + prompts
│   ├── data/           # Mock data + vector store
│   └── evaluation/     # Opik metrics and experiments
├── frontend/           # Streamlit UI
├── main.py             # FastAPI backend
└── requirements.txt    # Dependencies
```

## Quickstart
1) Create and activate a virtual environment
```bash
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Configure environment variables
Create a `.env` file in the repo root:
```
OPENAI_API_KEY=sk-...
OPIK_API_KEY=...
```

## RAG Data (Recommended Competition Set)
You can download documents locally (recommended) and ingest them into ChromaDB.

Recommended set (5 merchants + regulations):
- app/data/documents/netflix_terms.pdf
- app/data/documents/planet_fitness_terms.pdf
- app/data/documents/adobe_terms.pdf
- app/data/documents/spotify_terms.pdf
- app/data/documents/amazon_terms.pdf
- app/data/documents/ftc_negative_option_rule.pdf
- app/data/documents/state_consumer_protection.pdf

Download locally:
```bash
python scripts/download_documents.py
```

Ingest into ChromaDB:
```bash
python app/data/vector_db.py
```

Notes:
- The downloader may fetch HTML pages; ingestion handles PDF/HTML/TXT.
- Do not commit the downloaded PDFs or `app/data/chroma_db_store`.

## Run the App
Terminal 1 (Backend):
```bash
python main.py
```

Terminal 2 (Frontend):
```bash
streamlit run frontend/ui.py
```

UI note: after analysis, a **Draft the letter** button appears to confirm intent before letter generation.

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

## Roadmap
- Frontend upgrade to React/Next.js
- Deeper multi-turn negotiation workflows
- Expanded datasets and scenario coverage

## License
MIT
