import os
from typing import Any, Dict, List, Optional

import opik
from dotenv import load_dotenv
from openai import OpenAI
from opik import track

from app.agent.graph import build_graph, run_graph
from app.data.vector_db import LegalKnowledgeBase

# LOAD ENV & OPIK
load_dotenv()
opik.configure(use_local=False)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

try:
    kb = LegalKnowledgeBase()
except Exception:
    kb = None

_graph_app = build_graph(client, kb)


@track(name="Fiscal_Sentinel_Run")
def run_sentinel(
    user_input: str,
    transactions: List[Dict[str, Any]],
    history: Optional[List[Dict[str, str]]] = None,
    debug: bool = False,
):
    messages = history[:] if history else []
    messages.append({"role": "user", "content": user_input})

    state = {
        "messages": messages,
        "user_input": user_input,
        "transactions": transactions,
    }
    result = run_graph(_graph_app, state)
    response = result.get("final_response", "")
    if not debug:
        return response

    query = result.get("transaction_query")
    debug_payload = {
        "intent": result.get("intent"),
        "wants_retrieval": result.get("wants_retrieval"),
        "wants_letter": result.get("wants_letter"),
        "needs_evidence": result.get("needs_evidence"),
        "transaction_query_type": getattr(query, "query_type", None),
        "needs_followup": getattr(query, "needs_followup", None),
        "retrieval_used": bool(result.get("retrieval_context")),
    }
    return response, debug_payload
