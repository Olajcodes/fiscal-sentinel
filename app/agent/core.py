import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import opik
from opik import track
from app.agent.prompts import FISCAL_SENTINEL_PROMPT

# LOAD ENV & RAG
load_dotenv()
opik.configure(use_local=False)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# CHECK RAG
try:
    from app.data.vector_db import LegalKnowledgeBase
    kb = LegalKnowledgeBase()
    has_rag = True
except:
    has_rag = False

# --- TOOLS ---
@track
def retrieve_laws(query: str):
    """Searches legal docs."""
    print(f"🔎 TOOL CALL: Searching laws for '{query}'...")
    if has_rag: return kb.search_laws(query)
    return "Mock Law: FTC Rule 404 - Notifications required."

@track
def draft_letter(merchant: str, issue: str):
    """Drafts a letter."""
    print(f"✍️ TOOL CALL: Drafting letter for {merchant}...")
    return f"To {merchant}:\nWe formally dispute the charge regarding {issue}.\nSigned, Fiscal Sentinel."

# --- TOOL DEFINITIONS (OpenAI Format) ---
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_laws",
            "description": "Search for relevant consumer protection laws.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Legal topic to search"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "draft_letter",
            "description": "Draft a formal dispute or cancellation letter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "merchant": {"type": "string"},
                    "issue": {"type": "string"}
                },
                "required": ["merchant", "issue"]
            }
        }
    }
]

# --- MAIN AGENT ---
@track(name="Fiscal_Sentinel_Run")
def run_sentinel(user_input: str, transactions: list):
    # Prepare Context
    tx_context = json.dumps(transactions, indent=2)
    messages = [
        {"role": "system", "content": FISCAL_SENTINEL_PROMPT},
        {"role": "user", "content": f"TRANSACTIONS:\n{tx_context}\n\nUSER REQUEST:\n{user_input}"}
    ]

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Stable and fast
        messages=messages,
        tools=tools_schema,
        tool_choice="auto" 
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Handle Tool Calls
    if tool_calls:
        # Append the model's request to history
        messages.append(response_message)
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute Tool
            function_response = ""
            if function_name == "retrieve_laws":
                function_response = retrieve_laws(query=function_args.get("query"))
            elif function_name == "draft_letter":
                function_response = draft_letter(
                    merchant=function_args.get("merchant"),
                    issue=function_args.get("issue")
                )
            
            # Feed back to model
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": function_response,
            })

        # Final Answer
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return second_response.choices[0].message.content

    return response_message.content