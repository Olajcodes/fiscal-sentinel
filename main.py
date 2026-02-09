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
from app.data.vector_db import LegalKnowledgeBase
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from app.services import auth_services
from app.services.conversation_services import (
    HISTORY_LIMIT,
    append_messages,
    get_history,
    get_or_create_conversation,
)

app = FastAPI(
    title="Fiscal Sentinel API",
    description="Backend API for transaction analysis, document ingestion, and dispute-letter assistance.",
    version="1.0.0",
)




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Request(BaseModel):
    query: str
    history: list | None = None
    debug: bool | None = False
    conversation_id: str | None = None
    user_id: str | None = None


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
    notes: list[str] | None = None
    preview_schema: PreviewSchema = Field(alias="schema")
    confidence_stats: dict


@app.get("/", summary="Health check", description="Basic health endpoint.")
def root():
    return {"message": "Fiscal Sentinel API up and running"}

# Auth Routes
@app.post(
    "/register",
    status_code=201,
    summary="Register user",
    description="Create a new user account.",
    tags=["auth"],
)
async def register_user(payload: auth_services.UserCreate):
    return await auth_services.AuthService.register_user(payload)

@app.post(
    "/login",
    summary="Login user",
    description="Authenticate a user and return a login response.",
    tags=["auth"],
)
async def login_user(payload: auth_services.UserLogin):
    return await auth_services.AuthService.login_user(payload)

# User Routes
@app.get(
    "/users",
    summary="List users",
    description="Return all users in the database.",
    tags=["users"],
)
async def get_all_users():
    return await auth_services.UserService.get_all_users()

@app.get(
    "/users/{user_id}",
    summary="Get user",
    description="Return a single user by ID.",
    tags=["users"],
)
async def get_user(user_id: str):
    return await auth_services.UserService.get_user(user_id)

@app.put(
    "/users/{user_id}",
    summary="Update user",
    description="Replace a user document by ID.",
    tags=["users"],
)
async def update_user(user_id: str, payload: auth_services.UserUpdate):
    return await auth_services.UserService.update_user(user_id, payload)

@app.patch(
    "/users/{user_id}",
    summary="Patch user",
    description="Partially update a user document by ID.",
    tags=["users"],
)
async def patch_user(user_id: str, payload: auth_services.UserPatch):
    return await auth_services.UserService.patch_user(user_id, payload)

@app.delete(
    "/users/{user_id}",
    status_code=204,
    summary="Delete user",
    description="Delete a user by ID.",
    tags=["users"],
)
async def delete_user(user_id: str):
    await auth_services.UserService.delete_user(user_id)



    




@app.get(
    "/transactions",
    summary="List transactions",
    description="Return stored transactions or fall back to mock data.",
    tags=["transactions"],
)
def get_tx():
    stored = load_transactions()
    return stored if stored else get_mock_transactions()

@app.post(
    "/transactions/preview",
    response_model=PreviewResponse,
    summary="Preview transactions upload",
    description="Parse a CSV/PDF upload and return columns, sample rows, and mapping suggestions.",
    tags=["transactions"],
)
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
        "notes": preview.get("notes", []),
        "schema": preview.get("schema", {}),
        "confidence_stats": preview.get(
            "confidence_stats",
            {"avg": 0.0, "min": 0.0, "max": 0.0, "count": 0},
        ),
    }

@app.post(
    "/transactions/confirm",
    summary="Confirm transaction mapping",
    description="Apply a user-provided column mapping to the preview and persist transactions.",
    tags=["transactions"],
)
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

@app.post(
    "/transactions/upload",
    summary="Upload transactions",
    description="Upload a CSV or PDF and persist parsed transactions directly.",
    tags=["transactions"],
)
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

@app.post(
    "/analyze",
    summary="Analyze query",
    description="Run the agent over a user query and current transactions.",
    tags=["analysis"],
)
async def analyze(req: Request):
    try:
        tx = load_transactions() or get_mock_transactions()
        history = req.history or []
        conversation_id = req.conversation_id
        user_id = req.user_id

        if conversation_id or req.history is None:
            conversation_id = await get_or_create_conversation(conversation_id, user_id)
            history = await get_history(conversation_id, limit=HISTORY_LIMIT, user_id=user_id)

        if req.debug:
            response, debug_payload = run_sentinel(req.query, tx, history=history, debug=True)
            new_messages = [
                {"role": "user", "content": req.query},
                {"role": "assistant", "content": response},
            ]
            history_out = (history + new_messages)[-HISTORY_LIMIT:]
            if conversation_id:
                await append_messages(
                    conversation_id,
                    new_messages,
                    limit=HISTORY_LIMIT,
                    user_id=user_id,
                )
            return {
                "response": response,
                "debug": debug_payload,
                "conversation_id": conversation_id,
                "history": history_out,
            }

        response = run_sentinel(req.query, tx, history=history)
        new_messages = [
            {"role": "user", "content": req.query},
            {"role": "assistant", "content": response},
        ]
        history_out = (history + new_messages)[-HISTORY_LIMIT:]
        if conversation_id:
            await append_messages(
                conversation_id,
                new_messages,
                limit=HISTORY_LIMIT,
                user_id=user_id,
            )
        return {
            "response": response,
            "conversation_id": conversation_id,
            "history": history_out,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.get(
    "/vector-db/health",
    summary="Vector DB health",
    description="Report active vector DB provider, collection, and vector count.",
    tags=["infra"],
)
def vector_db_health():
    try:
        kb = LegalKnowledgeBase()
        stats = kb.get_collection_stats()
        return {"provider": kb.provider, "collection": kb.collection_name, **stats}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
