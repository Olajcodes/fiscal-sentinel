from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from app.database import conversations_collection

HISTORY_LIMIT = 20


def _now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _sanitize_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    cleaned: List[Dict[str, str]] = []
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = (msg.get("role") or "").strip()
        content = (msg.get("content") or "").strip()
        if role and content:
            cleaned.append({"role": role, "content": content, "ts": _now_iso()})
    return cleaned


async def get_or_create_conversation(conversation_id: Optional[str], user_id: Optional[str]) -> str:
    query: Dict[str, str] = {}
    if conversation_id:
        query["conversation_id"] = conversation_id
        if user_id:
            existing_any = await conversations_collection.find_one({"conversation_id": conversation_id})
            if existing_any and existing_any.get("user_id") and existing_any.get("user_id") != user_id:
                conversation_id = None
                query = {}
    if user_id:
        query["user_id"] = user_id
    if query:
        existing = await conversations_collection.find_one(query)
        if existing:
            return existing["conversation_id"]

    conversation_id = conversation_id or str(uuid4())
    doc = {
        "conversation_id": conversation_id,
        "messages": [],
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    if user_id:
        doc["user_id"] = user_id
    await conversations_collection.insert_one(doc)
    return conversation_id


async def append_messages(
    conversation_id: str,
    messages: List[Dict[str, str]],
    limit: int = HISTORY_LIMIT,
    user_id: Optional[str] = None,
) -> None:
    cleaned = _sanitize_messages(messages)
    if not cleaned:
        return
    query: Dict[str, str] = {"conversation_id": conversation_id}
    if user_id:
        query["user_id"] = user_id
    await conversations_collection.update_one(
        query,
        {
            "$push": {"messages": {"$each": cleaned, "$slice": -abs(limit)}},
            "$set": {"updated_at": _now_iso()},
            "$setOnInsert": {
                "created_at": _now_iso(),
                **({"user_id": user_id} if user_id else {}),
            },
        },
        upsert=True,
    )


async def get_history(
    conversation_id: str,
    limit: int = HISTORY_LIMIT,
    user_id: Optional[str] = None,
) -> List[Dict[str, str]]:
    query: Dict[str, str] = {"conversation_id": conversation_id}
    if user_id:
        query["user_id"] = user_id
    doc = await conversations_collection.find_one(query, {"messages": {"$slice": -abs(limit)}})
    if not doc or not doc.get("messages"):
        return []
    history: List[Dict[str, str]] = []
    for msg in doc.get("messages", []):
        role = msg.get("role")
        content = msg.get("content")
        if role and content:
            history.append({"role": role, "content": content})
    return history
