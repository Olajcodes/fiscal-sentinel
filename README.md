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

## Sample Upload Files
Use these to test the upload flow and analyzer:
- app/data/examples/transactions_sample.csv
- app/data/examples/transactions_sample.json

Upload via the UI sidebar or POST to `/transactions/upload`.

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

## PDF Statement Uploads
For bank statements in PDF, the upload parser uses `camelot` (text-based PDFs). If the statement is scanned (image-only),
the system falls back to OCR using `pdf2image` + `pytesseract`.

OCR prerequisites (system installs):
- Poppler (for `pdf2image`)
- Tesseract OCR (for `pytesseract`)

If Poppler is unavailable, OCR falls back to PyMuPDF rendering. You can also set
`POPPLER_PATH` and/or `TESSERACT_CMD` to point to the installed binaries. If OCR
still fails, export a CSV/JSON from your bank instead.

## Transaction Upload Preview API
For complex PDFs, use a preview step to confirm columns:

1) Preview (returns suggested mapping + sample rows)
```bash
curl -F "file=@/path/to/statement.pdf" http://localhost:8000/transactions/preview
```

2) Confirm (send mapping from preview)
```bash
curl -X POST http://localhost:8000/transactions/confirm \
  -H "Content-Type: application/json" \
  -d '{"preview_id":"<id>","mapping":{"date":"date_time","money_out":"money_out","money_in":"money_in","merchant_name":"party","description":"description","category":"category"}}'
```

Preview response includes a `schema` object describing target fields (e.g., `date`, `money_in`, `merchant_name`) so
frontends can build a generic column-mapper UI. OCR rows may include a `confidence` score (0.0–1.0) to flag low-quality parses.
The preview response also returns `confidence_stats` (avg/min/max/count) for quick quality checks.

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
Got it 👍 — this should **sit alongside your general README**, not repeat it.

Below is a **frontend-specific `README.md`** that is clearly scoped to the **UI layer only**, assumes the backend exists (or will), and is written the way a serious startup/frontend repo would be.

---

```md
# Fiscal Sentinel — Frontend (User Interface)

This repository contains the **frontend user interface** for **Fiscal Sentinel**, built with **Next.js App Router**, **TypeScript**, and **Tailwind CSS**.

The frontend is responsible for:
- Public-facing marketing pages
- Application layout and navigation
- User interaction and UI state
- Preparing integration points for backend APIs and AI services

> This README intentionally focuses **only on the frontend**.  
> For product vision, backend architecture, and system-wide details, refer to the main project README.

---

## 🎯 Purpose of the Frontend

The Fiscal Sentinel UI is designed to:
- Communicate trust (fintech-grade UX)
- Clearly explain value to users
- Provide a scalable base for dashboards, alerts, and dispute workflows
- Remain modular as product features evolve

---

## 🧱 Tech Stack

- **Framework:** Next.js (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Routing:** App Router with route groups
- **State Strategy:** Layout-driven (API-ready)
- **Deployment Target:** Vercel

---

##  Frontend Structure

```

app/
├── layout.tsx              # Global application layout
├── globals.css             # Tailwind + global styles
│
├── (external pages)/             # Public-facing pages (landing, marketing)
│   ├── layout.tsx          # External pages layout
│   └── page.tsx            # Landing page
│
├── (dashboard)/            # Authenticated app area (in progress)
│   ├── layout.tsx
│   └── page.tsx
│
└── api/                    # Frontend API routes (in progress)

````

---

## Layout Strategy

### Global Layout
`app/layout.tsx`
- Global fonts
- Metadata
- Providers (future auth, theme, state)
- Shared UI elements

### External Pages Layout
`app/(external pages)/layout.tsx`
- Clean separation for external pages


---

##  Local Development

### Install dependencies
```bash
npm install
# or
yarn install
````

### Start development server

```bash
npm run dev
# or
yarn dev
```

Access the app at:

```
http://localhost:3000
```

---

##  Styling Guidelines

* Tailwind CSS is the primary styling system
* Global styles live in `app/globals.css`
* Prefer **layout-level styling** over page-level overrides
* Keep components presentational and reusable


Design tokens and CSS variables can be introduced for theming as the UI matures.

---

##  Environment Variables (Frontend)

Create a `.env.local` file:

```env
NEXT_PUBLIC_APP_NAME=Fiscal Sentinel
```

Only **public-safe variables** should be exposed here.
Sensitive credentials must never live in the frontend.

---

## Backend Integration (Planned)

The frontend is structured to integrate cleanly with:

* Authentication services
* Financial data providers
* AI-powered analysis endpoints
* Dispute letter generation services

All integrations will be introduced behind typed API layers.

---

## 📦 Production Build

```bash
npm run build
npm run start
```

Recommended hosting: **Vercel**

---

## 🧠 Frontend Roadmap

* Authenticated dashboard UI
* Transaction and subscription views
* Alerts & savings insights
* Dispute letter preview and export UI
* Accessibility and performance hardening
* Fintech-grade UX polish

---

## 📜 License

Private / Proprietary
(Frontend codebase — subject to change)

---



