import json
import re
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph
from openai import OpenAI
from opik import track
from opik.opik_context import update_current_span

from app.agent.prompts import (
    FISCAL_SENTINEL_ANALYSIS_PROMPT,
    FISCAL_SENTINEL_ASSISTANT_PROMPT,
    FISCAL_SENTINEL_COMPOSER_PROMPT,
    FISCAL_SENTINEL_LETTER_PROMPT,
    FISCAL_SENTINEL_ROUTER_PROMPT,
)
from app.analysis.transaction_analyzer import analyze_transactions_rule_based
from app.analysis.transaction_query import answer_transaction_query, parse_transaction_query, TransactionQuery
from app.data.vector_db import LegalKnowledgeBase


class AgentState(TypedDict, total=False):
    messages: List[Dict[str, str]]
    user_input: str
    transactions: List[Dict[str, Any]]
    intent: str
    wants_letter: bool
    wants_retrieval: bool
    transaction_query: TransactionQuery
    transaction_answer: str
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


def _safe_span_update(metadata: Dict[str, Any]) -> None:
    try:
        update_current_span(metadata=metadata)
    except Exception:
        return


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _explicit_letter_request(text: str) -> bool:
    patterns = [
        "draft a letter",
        "draft letter",
        "write a letter",
        "write letter",
        "compose a letter",
        "generate a letter",
        "send a letter",
        "letter of dispute",
        "dispute letter",
        "cancellation letter",
        "cancelation letter",
        "termination letter",
    ]
    if any(p in text for p in patterns):
        return True
    verbs = ["draft", "write", "compose", "generate", "create", "send"]
    nouns = ["letter", "cancellation", "cancelation", "dispute", "complaint", "termination", "notice"]
    return any(v in text for v in verbs) and any(n in text for n in nouns)


def _is_affirmative(text: str) -> bool:
    affirmations = {
        "yes",
        "yes please",
        "please do",
        "do it",
        "go ahead",
        "sure",
        "ok",
        "okay",
    }
    return text in affirmations or text.startswith("yes ")


def _assistant_asked_to_draft(messages: List[Dict[str, str]]) -> bool:
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            content = _normalize_text(msg.get("content", ""))
            return ("draft" in content and "letter" in content) or (
                "write" in content and "letter" in content
            )
    return False


def _wants_legal_help(text: str) -> bool:
    normalized = _normalize_text(text)
    phrases = [
        "is it legal",
        "can i fight",
        "fight it",
        "fight this",
    ]
    if any(p in normalized for p in phrases):
        return True
    tokens = set(re.findall(r"[a-z]+", normalized))
    keywords = {
        "legal",
        "law",
        "regulation",
        "ftc",
        "rights",
        "statute",
        "rule",
    }
    return any(word in tokens for word in keywords)


def _wants_analysis(text: str) -> bool:
    triggers = [
        "analyze",
        "scan",
        "check",
        "review",
        "look over",
        "subscriptions",
        "transactions",
        "transaction",
        "charges",
        "fees",
        "bank feed",
        "statement",
    ]
    return any(t in text for t in triggers)


def _normalize_merchant(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    base = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    if "planet" in base and "fitness" in base:
        return "planet_fitness"
    if "netflix" in base:
        return "netflix"
    if "adobe" in base:
        return "adobe"
    if "spotify" in base:
        return "spotify"
    if "amazon" in base:
        return "amazon"
    if "ftc" in base:
        return "ftc"
    return base


def _detect_merchant_from_text(text: str) -> Optional[str]:
    normalized = _normalize_text(text)
    if "planet" in normalized and "fitness" in normalized:
        return "planet_fitness"
    for name in ["netflix", "adobe", "spotify", "amazon", "ftc"]:
        if name in normalized:
            return name
    return None


def _basic_intent_heuristic(user_input: str, messages: List[Dict[str, str]]) -> Optional[str]:
    text = _normalize_text(user_input)
    if re.fullmatch(r"(hi|hello|hey|good morning|good afternoon|good evening)[!. ]*", text):
        return "greeting"
    if _explicit_letter_request(text):
        return "draft_letter"
    if _is_affirmative(text) and _assistant_asked_to_draft(messages):
        return "draft_letter"
    if _wants_legal_help(text):
        return "retrieve_laws"
    if _wants_analysis(text):
        return "analyze_transactions"
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
        messages = state.get("messages", [])
        tx = state.get("transactions", [])
        normalized = _normalize_text(user_input)
        wants_letter = _explicit_letter_request(normalized) or (
            _is_affirmative(normalized) and _assistant_asked_to_draft(messages)
        )
        wants_retrieval = _wants_legal_help(normalized) or wants_letter

        transaction_query = parse_transaction_query(user_input, tx)
        if transaction_query and not wants_letter and not _wants_legal_help(normalized):
            _safe_span_update(
                {
                    "intent": "transaction_query",
                    "wants_retrieval": False,
                    "transaction_query_type": transaction_query.query_type,
                    "needs_followup": transaction_query.needs_followup,
                }
            )
            return {
                "intent": "transaction_query",
                "wants_letter": wants_letter,
                "wants_retrieval": False,
                "transaction_query": transaction_query,
            }

        heuristic = _basic_intent_heuristic(user_input, messages)
        if heuristic:
            _safe_span_update(
                {
                    "intent": heuristic,
                    "wants_retrieval": wants_retrieval or heuristic == "retrieve_laws",
                }
            )
            return {
                "intent": heuristic,
                "wants_letter": wants_letter or heuristic == "draft_letter",
                "wants_retrieval": wants_retrieval or heuristic == "retrieve_laws",
            }

        history = messages[-6:] if messages else [{"role": "user", "content": user_input}]
        router_messages = [{"role": "system", "content": FISCAL_SENTINEL_ROUTER_PROMPT}] + history
        result = _openai_json_response(client, router_messages)
        intent = result.get("intent") or "other"
        explicit_legal = _wants_legal_help(normalized)
        if intent == "draft_letter" and not wants_letter:
            intent = "general_question"
        if intent == "retrieve_laws" and not explicit_legal and not wants_letter:
            intent = "analyze_transactions" if _wants_analysis(normalized) else "general_question"
        wants_retrieval = explicit_legal or wants_letter
        _safe_span_update(
            {
                "intent": intent,
                "wants_retrieval": wants_retrieval or intent == "retrieve_laws",
            }
        )
        return {
            "intent": intent,
            "wants_letter": wants_letter or intent == "draft_letter",
            "wants_retrieval": wants_retrieval or intent in ["retrieve_laws", "draft_letter"],
        }

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

    @track(name="transaction_query")
    def transaction_query_node(state: AgentState) -> AgentState:
        query = state.get("transaction_query")
        tx = state.get("transactions", [])
        if not query:
            return {"final_response": "Can you clarify what you want to know about your transactions?"}
        response = answer_transaction_query(query, tx)
        _safe_span_update(
            {
                "transaction_query_type": query.query_type,
                "needs_followup": query.needs_followup,
                "wants_retrieval": False,
            }
        )
        return {"final_response": response}

    @track(name="analyze_transactions")
    def analyze_transactions(state: AgentState) -> AgentState:
        user_input = state.get("user_input", "")
        tx = state.get("transactions", [])
        rule_based_issues = analyze_transactions_rule_based(tx)
        if rule_based_issues:
            needs_evidence = bool(state.get("wants_retrieval") or state.get("wants_letter"))
            return {
                "analysis": {"issues": rule_based_issues},
                "needs_evidence": needs_evidence,
            }
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
        merchant = None
        if issues:
            issue = issues[0]
            issue_text = f"{issue.get('merchant', '')} - {issue.get('issue', '')}"
            merchant = _normalize_merchant(issue.get("merchant"))
        else:
            merchant = _detect_merchant_from_text(user_input)
        query = f"{user_input}\n{issue_text}".strip()
        context = kb.search_laws(query, merchant=merchant) if query else ""
        _safe_span_update({"retrieval_used": True, "merchant": merchant or ""})
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
        wants_letter = state.get("wants_letter", False)
        needs_evidence = state.get("needs_evidence", False)

        payload = {
            "intent": intent,
            "assistant_response": assistant_response,
            "analysis": analysis,
            "retrieval_context": retrieval_context,
            "letter": letter,
            "wants_letter": wants_letter,
            "needs_evidence": needs_evidence,
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
        if intent == "transaction_query":
            return "transaction_query"
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
        if state.get("final_response"):
            return END
        wants_letter = state.get("wants_letter", False)
        wants_retrieval = state.get("wants_retrieval", False)
        issues = (state.get("analysis") or {}).get("issues") or []
        if wants_letter:
            return "retrieve_laws"
        if wants_retrieval and issues:
            return "retrieve_laws"
        return "compose"

    def route_after_retrieve(state: AgentState) -> str:
        return "draft_letter" if state.get("wants_letter") else "compose"

    @track(name="finalize_assistant")
    def finalize_assistant(state: AgentState) -> AgentState:
        return {"final_response": state.get("assistant_response", "")}

    graph.add_node("router", router)
    graph.add_node("assistant", assistant)
    graph.add_node("transaction_query", transaction_query_node)
    graph.add_node("analyze_transactions", analyze_transactions)
    graph.add_node("retrieve_laws", retrieve_laws)
    graph.add_node("draft_letter", draft_letter)
    graph.add_node("compose", compose)
    graph.add_node("finalize_assistant", finalize_assistant)

    graph.set_entry_point("router")
    graph.add_conditional_edges("router", route_after_router)
    graph.add_conditional_edges("analyze_transactions", route_after_analysis)
    graph.add_conditional_edges("retrieve_laws", route_after_retrieve)

    graph.add_edge("assistant", "finalize_assistant")
    graph.add_edge("draft_letter", "compose")

    graph.add_edge("compose", END)
    graph.add_edge("finalize_assistant", END)

    return graph.compile()


def run_graph(app, state: AgentState) -> AgentState:
    return app.invoke(state)
