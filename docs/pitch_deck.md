# Fiscal Sentinel Pitch Deck (10 Slides)

## 1. Title
- Fiscal Sentinel
- One-liner: Fiscal Sentinel finds suspicious subscription charges in your bank statement and drafts dispute letters using verified policy evidence.
- Team name and contact

## 2. Problem
- Consumers struggle to identify questionable charges.
- Cancellation and dispute processes are confusing and evidence-heavy.
- Result: lost money and time.

## 3. Solution
- Upload statement, get suspicious charges, and draft letters with citations.
- Retrieval only when user asks about legality or requests a letter.

## 4. Demo Snapshot
- Upload preview and column mapping
- Deterministic Q and A (highest, totals, by-merchant)
- Letter drafting with evidence

## 5. How It Works
- Transaction parsing and normalization
- Agent routing with strict retrieval gating
- Vector search over merchant terms and regulations

## 6. Evidence and Trust
- Citations come from verified policy docs
- Opik tracing for transparency and auditability

## 7. Metrics (Opik)
- Retrieval discipline (no random citations)
- Response actionability
- Conversation quality
- Legal citation precision

## 8. Tech Stack
- FastAPI + LangGraph
- Qdrant + OpenAI embeddings
- Next.js web UI
- Opik evaluation

## 9. Roadmap
- Bank sync integrations
- More merchants and regional regulations
- Export-ready letters and workflows

## 10. Ask
- Judges: evaluate clarity, safety, and evidence quality
- Partners: provide additional policy docs for broader coverage
