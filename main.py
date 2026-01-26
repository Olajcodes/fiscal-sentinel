# This is the Entry point (FastAPI app)

from fastapi import FastAPI
from pydantic import BaseModel
from app.agent.core import run_sentinel
from app.data.mock_plaid import get_mock_transactions
import uvicorn

app = FastAPI()

class Request(BaseModel):
    query: str

@app.get("/transactions")
def get_tx():
    return get_mock_transactions()

@app.post("/analyze")
def analyze(req: Request):
    tx = get_mock_transactions()
    res = run_sentinel(req.query, tx)
    return {"response": res}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)