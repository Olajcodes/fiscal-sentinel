# This is the Entry point (FastAPI app)

from fastapi import FastAPI
from pydantic import BaseModel
from app.agent.core import run_sentinel
from app.data.mock_plaid import get_mock_transactions
import uvicorn




# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services import auth_services

from app.services.auth_services import (
    UserCreate, UserLogin, UserUpdate, UserPatch,
    
)

app = FastAPI(title="Learning Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app = FastAPI()

class Request(BaseModel):
    query: str
    history: list | None = None



@app.get("/")
def root():
    return {"message": "Fiscal Sentinel API up and running"}






# Auth Routes
@app.post("/register", status_code=201)
async def register_user(payload: UserCreate):
    return await auth_services.AuthService.register_user(payload)

@app.post("/login")
async def login_user(payload: UserLogin):
    return await auth_services.AuthService.login_user(payload)

# User Routes
@app.get("/users")
async def get_all_users():
    return await auth_services.UserService.get_all_users()

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    return await auth_services.UserService.get_user(user_id)

@app.put("/users/{user_id}")
async def update_user(user_id: str, payload: UserUpdate):
    return await auth_services.UserService.update_user(user_id, payload)

@app.patch("/users/{user_id}")
async def patch_user(user_id: str, payload: UserPatch):
    return await auth_services.UserService.patch_user(user_id, payload)

@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: str):
    await auth_services.UserService.delete_user(user_id)





@app.get("/transactions")
def get_tx():
    return get_mock_transactions()

@app.post("/analyze")
def analyze(req: Request):
    tx = get_mock_transactions()
    res = run_sentinel(req.query, tx, history=req.history)
    return {"response": res}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
