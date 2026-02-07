from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict

DATA_DIR = Path(__file__).resolve().parent
PREVIEW_DIR = DATA_DIR / "previews"


def save_preview(payload: Dict[str, Any]) -> str:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    preview_id = uuid.uuid4().hex
    path = PREVIEW_DIR / f"{preview_id}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return preview_id


def load_preview(preview_id: str) -> Dict[str, Any]:
    path = PREVIEW_DIR / f"{preview_id}.json"
    if not path.exists():
        raise ValueError("Preview not found or expired.")
    return json.loads(path.read_text(encoding="utf-8") or "{}")


def delete_preview(preview_id: str) -> None:
    path = PREVIEW_DIR / f"{preview_id}.json"
    if path.exists():
        path.unlink()
