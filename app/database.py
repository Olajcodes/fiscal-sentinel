# app/db/db.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)
if DB_NAME:
    db = client[DB_NAME]

users_collection = db.users
admins_collection = db.admins
user_profiles_collection = db.user_profiles
conversations_collection = db.conversations
