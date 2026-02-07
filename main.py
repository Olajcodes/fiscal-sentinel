# This is the Entry point (FastAPI app)

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, Field
from app.agent.core import run_sentinel
from app.data.bank_transactions import (
    extract_rows_from_upload,
    load_transactions,
    normalize_rows_with_mapping,
    parse_transactions_from_upload,
    save_transactions,
)
from app.data.preview_store import delete_preview, load_preview, save_preview
from app.data.mock_plaid import get_mock_transactions
import uvicorn

app = FastAPI()

class Request(BaseModel):
    query: str
    history: list | None = None
    debug: bool | None = False


class PreviewConfirmRequest(BaseModel):
    preview_id: str
    mapping: dict


class PreviewSchemaField(BaseModel):
    name: str
    required: bool
    description: str


class PreviewSchema(BaseModel):
    target_fields: list[PreviewSchemaField]
    mapping_rules: dict


class PreviewResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    preview_id: str
    columns: list[str]
    sample_rows: list[dict]
    suggested_mapping: dict
    source: str
    preview_schema: PreviewSchema = Field(alias="schema")
    confidence_stats: dict

@app.get("/transactions")
def get_tx():
    stored = load_transactions()
    return stored if stored else get_mock_transactions()

@app.post("/transactions/preview", response_model=PreviewResponse)
async def preview_transactions(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="Missing file upload.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    try:
        preview = extract_rows_from_upload(file.filename or "", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    rows = preview.get("rows") or []
    columns = preview.get("columns") or []
    preview_id = save_preview({"rows": rows, "columns": columns})
    sample_rows = rows[:10]
    return {
        "preview_id": preview_id,
        "columns": columns,
        "sample_rows": sample_rows,
        "suggested_mapping": preview.get("suggested_mapping", {}),
        "source": preview.get("source", "unknown"),
        "schema": preview.get("schema", {}),
        "confidence_stats": preview.get(
            "confidence_stats",
            {"avg": 0.0, "min": 0.0, "max": 0.0, "count": 0},
        ),
    }

@app.post("/transactions/confirm")
def confirm_transactions(req: PreviewConfirmRequest):
    try:
        preview = load_preview(req.preview_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    rows = preview.get("rows") or []
    if not rows:
        raise HTTPException(status_code=400, detail="Preview contains no rows.")

    transactions = normalize_rows_with_mapping(rows, req.mapping)
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions produced from mapping.")

    save_transactions(transactions, source=f"preview:{req.preview_id}")
    delete_preview(req.preview_id)
    return {"count": len(transactions)}

@app.post("/transactions/upload")
async def upload_transactions(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="Missing file upload.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    try:
        transactions = parse_transactions_from_upload(file.filename or "", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions parsed from upload.")

    save_transactions(transactions, source=file.filename or "upload")
    return {"count": len(transactions)}

@app.post("/analyze")
def analyze(req: Request):
    try:
        tx = load_transactions() or get_mock_transactions()
        if req.debug:
            response, debug_payload = run_sentinel(req.query, tx, history=req.history, debug=True)
            return {"response": response, "debug": debug_payload}
        res = run_sentinel(req.query, tx, history=req.history)
        return {"response": res}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
