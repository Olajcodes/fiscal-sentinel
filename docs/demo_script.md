# Fiscal Sentinel Demo Script (3 Minutes)

## Goal
Show that Fiscal Sentinel can ingest statements, answer transaction questions deterministically, and draft evidence-backed letters only when requested.

## Prep
- Backend running (Railway or local).
- UI running (Next.js web app).
- Uploaded sample PDF or CSV ready.

## Script
0:00 to 0:30
- Open the UI.
- Point to the Connected API label to confirm production backend.
- Explain the purpose in one sentence.

0:30 to 1:20
- Upload a statement.
- If preview appears, confirm mapping and load transactions.
- Call out the confidence stats in the preview.

1:20 to 2:00
- Ask: "What is the highest transaction this month?"
- Show the deterministic result (no legal citations).

2:00 to 2:30
- Ask: "Netflix raised my price without asking. Is that legal?"
- Show that retrieval activates and evidence appears.

2:30 to 3:00
- Ask: "Draft a dispute letter for Netflix"
- Confirm the UI asks for intent and then drafts with citations.
- Close with the value: quick, evidence-backed consumer help.

## Backup Prompts
- "How much did I spend on Netflix last 30 days?"
- "List recurring charges over 20 dollars"
- "Show the lowest debit this week"
