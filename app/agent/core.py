# Main Gemini loop (run_sentinel)
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# OPIK IMPORTS
import opik
from opik import track

# IMPORT TOOLS & PROMPTS
try:
    from app.agent.prompts import FISCAL_SENTINEL_PROMPT
except ImportError:
    FISCAL_SENTINEL_PROMPT = "You are Fiscal Sentinel. Find lost money. Be aggressive."

try:
    from app.data.vector_db import LegalKnowledgeBase
    kb = LegalKnowledgeBase()
    has_rag = True
except:
    # Safe fallback if RAG isn't ready
    has_rag = False

load_dotenv()

# CONFIGURE OPIK
opik.configure(use_local=False)

# INITIALIZE GEMINI
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# --- DEFINE TOOLS ---

@track
def retrieve_laws(query: str):
    """Searches for consumer protection laws."""
    print(f"🔎 TOOL CALL: Searching laws for '{query}'...")
    if has_rag:
        return kb.search_laws(query)
    else:
        # Mock responses for testing
        return f"Found law regarding '{query}': Companies must notify users 30 days before price hikes (FTC Rule)."

@track
def draft_letter(merchant: str, issue: str):
    """Drafts a dispute letter."""
    print(f"✍️ TOOL CALL: Drafting letter for {merchant}...")
    return f"DRAFT SAVED: Formal dispute letter to {merchant} regarding {issue}."

# --- MAIN AGENT LOOP ---

@track(name="Fiscal_Sentinel_Run")
def run_sentinel(user_input: str, transactions: list):
    """
    Main entry point for the agent.
    """
    
    # 1. Define Tools
    tools = [
        types.Tool(function_declarations=[
            types.FunctionDeclaration(
                name="retrieve_laws",
                description="Search for relevant consumer protection laws.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(type="STRING", description="Legal topic to search")
                    },
                    required=["query"]
                )
            ),
            types.FunctionDeclaration(
                name="draft_letter",
                description="Draft a formal dispute or cancellation letter.",
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "merchant": types.Schema(type="STRING"),
                        "issue": types.Schema(type="STRING")
                    },
                    required=["merchant", "issue"]
                )
            )
        ])
    ]

    # 2. Build Context
    tx_context = json.dumps(transactions, indent=2)
    full_prompt = f"""
    {FISCAL_SENTINEL_PROMPT}
    
    TRANSACTION DATA:
    {tx_context}
    
    USER REQUEST:
    {user_input}
    """

    # 3. First Call to Gemini
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
        config=types.GenerateContentConfig(tools=tools)
    )

    # 4. Handle Tool Calls
    # We maintain a manual history list to feed back to the model
    chat_history = [
        types.Content(role="user", parts=[types.Part(text=full_prompt)]),
        types.Content(role="model", parts=response.candidates[0].content.parts)
    ]

    if response.function_calls:
        # COLLECT all tool outputs into a single text block
        # This prevents the "User, User, User" role error
        tool_outputs_text = "Here are the results from the tools you called:\n"
        
        for call in response.function_calls:
            tool_name = call.name
            tool_args = call.args
            
            # Execute
            tool_result = "Error executing tool"
            if tool_name == "retrieve_laws":
                tool_result = retrieve_laws(**tool_args)
            elif tool_name == "draft_letter":
                tool_result = draft_letter(**tool_args)
            
            tool_outputs_text += f"\n--- OUTPUT for {tool_name} ---\n{tool_result}\n"
        
        # Append the AGGREGATED result as ONE user message
        chat_history.append(
            types.Content(
                role="user", 
                parts=[types.Part(text=tool_outputs_text)]
            )
        )
        
        # 5. Final Answer
        final_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=chat_history
        )
        
        if final_response.text:
            return final_response.text
        else:
            return "⚠️ Agent executed tools but returned no text. (Check Safety Settings)"

    # If no tools were called, just return the first response
    if response.text:
        return response.text
    else:
        return "⚠️ Agent returned no text and no tool calls."