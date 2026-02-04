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
):
    messages = history[:] if history else []
    messages.append({"role": "user", "content": user_input})

    state = {
        "messages": messages,
        "user_input": user_input,
        "transactions": transactions,
    }
    result = run_graph(_graph_app, state)
    return result.get("final_response", "")
