import json
import re
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph
from openai import OpenAI
from opik import track

from app.agent.prompts import (
    FISCAL_SENTINEL_ANALYSIS_PROMPT,
    FISCAL_SENTINEL_ASSISTANT_PROMPT,
    FISCAL_SENTINEL_COMPOSER_PROMPT,
    FISCAL_SENTINEL_LETTER_PROMPT,
    FISCAL_SENTINEL_ROUTER_PROMPT,
)
from app.data.vector_db import LegalKnowledgeBase


class AgentState(TypedDict, total=False):
    messages: List[Dict[str, str]]
    user_input: str
    transactions: List[Dict[str, Any]]
    intent: str
    analysis: Dict[str, Any]
    needs_evidence: bool
    retrieval_context: str
    letter: str
    assistant_response: str
    final_response: str


def _safe_json_loads(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        return {}


def _basic_intent_heuristic(user_input: str) -> Optional[str]:
    text = user_input.lower().strip()
    if re.fullmatch(r"(hi|hello|hey|good morning|good afternoon|good evening)[!. ]*", text):
        return "greeting"
    if any(k in text for k in ["draft", "write a letter", "letter", "cancellation", "dispute"]):
        return "draft_letter"
    if any(k in text for k in ["analyze", "scan", "check", "review", "subscriptions", "transactions", "charges", "fees"]):
        return "analyze_transactions"
    if any(k in text for k in ["law", "legal", "regulation", "ftc", "is it legal", "can i fight"]):
        return "retrieve_laws"
    return None


def _openai_json_response(client: OpenAI, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    return _safe_json_loads(content)


def build_graph(client: OpenAI, kb: Optional[LegalKnowledgeBase] = None):
    graph = StateGraph(AgentState)

    @track(name="router")
    def router(state: AgentState) -> AgentState:
        user_input = state.get("user_input", "")
        heuristic = _basic_intent_heuristic(user_input)
        if heuristic:
            return {"intent": heuristic}

        messages = [
            {"role": "system", "content": FISCAL_SENTINEL_ROUTER_PROMPT},
            {"role": "user", "content": user_input},
        ]
        result = _openai_json_response(client, messages)
        intent = result.get("intent") or "other"
        return {"intent": intent}

    @track(name="assistant")
    def assistant(state: AgentState) -> AgentState:
        messages = state.get("messages", [])
        base = [{"role": "system", "content": FISCAL_SENTINEL_ASSISTANT_PROMPT}]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=base + messages,
        )
        content = response.choices[0].message.content or ""
        return {"assistant_response": content}

    @track(name="analyze_transactions")
    def analyze_transactions(state: AgentState) -> AgentState:
        user_input = state.get("user_input", "")
        tx = state.get("transactions", [])
        messages = [
            {"role": "system", "content": FISCAL_SENTINEL_ANALYSIS_PROMPT},
            {
                "role": "user",
                "content": f"USER REQUEST:\n{user_input}\n\nTRANSACTIONS:\n{json.dumps(tx, indent=2)}",
            },
        ]
        result = _openai_json_response(client, messages)
        issues = result.get("issues") or []
        needs_evidence = any(i.get("needs_evidence") for i in issues)
        return {"analysis": result, "needs_evidence": needs_evidence}

    @track(name="retrieve_laws")
    def retrieve_laws(state: AgentState) -> AgentState:
        if not kb:
            return {"retrieval_context": ""}
        user_input = state.get("user_input", "")
        issues = (state.get("analysis") or {}).get("issues") or []
        issue_text = ""
        if issues:
            issue = issues[0]
            issue_text = f"{issue.get('merchant', '')} - {issue.get('issue', '')}"
        query = f"{user_input}\n{issue_text}".strip()
        context = kb.search_laws(query) if query else ""
        return {"retrieval_context": context}

    @track(name="draft_letter")
    def draft_letter(state: AgentState) -> AgentState:
        issues = (state.get("analysis") or {}).get("issues") or []
        issue = issues[0] if issues else {}
        if not issue:
            extract_messages = [
                {
                    "role": "system",
                    "content": "Extract merchant and issue from the user request. Return JSON: {\"merchant\":\"...\",\"issue\":\"...\"}.",
                },
                {"role": "user", "content": state.get("user_input", "")},
            ]
            extracted = _openai_json_response(client, extract_messages)
            issue = {
                "merchant": extracted.get("merchant"),
                "issue": extracted.get("issue"),
            }
        evidence = state.get("retrieval_context", "")
        messages = [
            {"role": "system", "content": FISCAL_SENTINEL_LETTER_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "merchant": issue.get("merchant"),
                        "issue": issue.get("issue"),
                        "amount": issue.get("amount"),
                        "reason": issue.get("reason"),
                        "evidence": evidence,
                    },
                    indent=2,
                ),
            },
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        content = response.choices[0].message.content or ""
        return {"letter": content}

    @track(name="compose")
    def compose(state: AgentState) -> AgentState:
        intent = state.get("intent", "other")
        assistant_response = state.get("assistant_response", "")
        analysis = state.get("analysis") or {}
        retrieval_context = state.get("retrieval_context", "")
        letter = state.get("letter", "")

        payload = {
            "intent": intent,
            "assistant_response": assistant_response,
            "analysis": analysis,
            "retrieval_context": retrieval_context,
            "letter": letter,
        }
        messages = [
            {"role": "system", "content": FISCAL_SENTINEL_COMPOSER_PROMPT},
            {"role": "user", "content": json.dumps(payload, indent=2)},
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        content = response.choices[0].message.content or ""
        return {"final_response": content}

    def route_after_router(state: AgentState) -> str:
        intent = state.get("intent", "other")
        if intent in ["greeting", "general_question", "other"]:
            return "assistant"
        if intent == "analyze_transactions":
            return "analyze_transactions"
        if intent == "retrieve_laws":
            return "retrieve_laws"
        if intent == "draft_letter":
            return "retrieve_laws"
        return "assistant"

    def route_after_analysis(state: AgentState) -> str:
        return "retrieve_laws" if state.get("needs_evidence") else "compose"

    def route_after_retrieve(state: AgentState) -> str:
        return "draft_letter" if state.get("intent") == "draft_letter" else "compose"

    graph.add_node("router", router)
    graph.add_node("assistant", assistant)
    graph.add_node("analyze_transactions", analyze_transactions)
    graph.add_node("retrieve_laws", retrieve_laws)
    graph.add_node("draft_letter", draft_letter)
    graph.add_node("compose", compose)

    graph.set_entry_point("router")
    graph.add_conditional_edges("router", route_after_router)
    graph.add_conditional_edges("analyze_transactions", route_after_analysis)
    graph.add_conditional_edges("retrieve_laws", route_after_retrieve)

    graph.add_edge("assistant", "compose")
    graph.add_edge("draft_letter", "compose")

    graph.add_edge("compose", END)

    return graph.compile()


def run_graph(app, state: AgentState) -> AgentState:
    return app.invoke(state)
