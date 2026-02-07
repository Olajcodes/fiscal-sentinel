# app/services/auth_services.py
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
import hashlib
from app.database import users_collection, user_profiles_collection
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List




class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    firstName: str
    lastName: str
    role: str = Field(default="User")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    role: str
    isActive: bool

class UserPatch(BaseModel):
    email: Optional[EmailStr] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: Optional[str] = None
    isActive: Optional[bool] = None


today = datetime.now()

def date_days_ago(days):
    return (today - timedelta(days=days)).strftime("%Y-%m-%d")



ROLE_DEFAULTS = {
    "User": {
        "transactions": [
            {
            "transaction_id": "",
            "date": "",
            "merchant_name": "",
            "amount": 0.00,
            "category": ["Subscription"],
            "notes": "Previous months were $19.99. No notification email found." 
        },
        ],

       
       
    },
    "Clients": {
        "transactions": [
            {
            "transaction_id": "",
            "date": "",
            "merchant_name": "",
            "amount": 0.00,
            "category": ["Subscription"],
            "notes": "Previous months were $19.99. No notification email found." 
        },
        ],

         "notifications": [
            {
            "notification_id": "",
            "date": "",
            "sender": "Ai_Agent",
            "category": ["report"],
            "details": "Previous months were $19.99. No notification email found." 
        },
        ],
        
    },
    "Admins": {
        "transactions": [
            {
            "transaction_id": "",
            "date": "",
            "merchant_name": "",
            "amount": 0.00,
            "category": ["Subscription"],
            "notes": "Previous months were $19.99. No notification email found." 
        },
        ],

        
        
    },
}

async def seed_user_data(user_id: ObjectId, role: str):
    defaults = ROLE_DEFAULTS.get(role, ROLE_DEFAULTS["User"])

    # Create user profile
    await user_profiles_collection.insert_one({
        "user_id": user_id,
        "role": role,
        "created_at": datetime.utcnow(),
    })

    

  



def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

def validate_object_id(user_id: str) -> ObjectId:
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Invalid user ID"},
        )
    return ObjectId(user_id)

def serialize_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "firstName": user.get("first_name"),
        "lastName": user.get("last_name"),
        "role": user.get("role", "User"),
        "isActive": user.get("is_active", True),
    }

def serialize_profile(profile: dict) -> dict:
    return {
        "id": str(profile["_id"]),
        "userId": str(profile["user_id"]),
        "role": profile["role"],
        "createdAt": profile["created_at"],
    }

class AuthService:
    
    @staticmethod
    async def register_user(payload: UserCreate):
        if await users_collection.find_one({"email": payload.email}):
            raise HTTPException(
                status_code=400,
                detail={"message": "Email already registered"},
            )

        user = {
            "email": payload.email,
            "password": hash_password(payload.password),
            "first_name": payload.firstName,
            "last_name": payload.lastName,
            "role": payload.role,
            "is_active": True,
            "created_at": datetime.utcnow(),
        }

        result = await users_collection.insert_one(user)
        user["_id"] = result.inserted_id

        await seed_user_data(user["_id"], payload.role)

        return {
            "message": "User registered successfully",
            "data": serialize_user(user),
        }
    
    @staticmethod
    async def login_user(payload: UserLogin):
        user = await users_collection.find_one({"email": payload.email})

        if not user or not verify_password(payload.password, user["password"]):
            raise HTTPException(
                status_code=401,
                detail={"message": "Invalid email or password"},
            )

        return {
            "message": "Login successful",
            "data": serialize_user(user),
        }

class UserService:
    
    @staticmethod
    async def get_all_users():
        users = []
        async for user in users_collection.find():
            users.append(serialize_user(user))

        return {
            "message": "Users fetched successfully",
            "data": users,
        }
    
    @staticmethod
    async def get_user(user_id: str):
        oid = validate_object_id(user_id)

        user = await users_collection.find_one({"_id": oid})
        if not user:
            raise HTTPException(
                status_code=404,
                detail={"message": "User not found"},
            )

        profile = await user_profiles_collection.find_one({"user_id": oid})
       

        return {
            "message": "User fetched successfully",
            "data": {
                "user": serialize_user(user),
                "profile": serialize_profile(profile) if profile else None,
            },
        }
    
    @staticmethod
    async def update_user(user_id: str, payload: UserUpdate):
        oid = validate_object_id(user_id)

        result = await users_collection.update_one(
            {"_id": oid},
            {"$set": {
                "email": payload.email,
                "first_name": payload.firstName,
                "last_name": payload.lastName,
                "role": payload.role,
                "is_active": payload.isActive,
            }},
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail={"message": "User not found"},
            )

        user = await users_collection.find_one({"_id": oid})

        return {
            "message": "User updated successfully",
            "data": serialize_user(user),
        }
    
    @staticmethod
    async def patch_user(user_id: str, payload: UserPatch):
        oid = validate_object_id(user_id)

        update_data = {}

        if payload.email is not None:
            update_data["email"] = payload.email
        if payload.firstName is not None:
            update_data["first_name"] = payload.firstName
        if payload.lastName is not None:
            update_data["last_name"] = payload.lastName
        if payload.role is not None:
            update_data["role"] = payload.role
        if payload.isActive is not None:
            update_data["is_active"] = payload.isActive

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail={"message": "No fields provided for update"},
            )

        result = await users_collection.update_one(
            {"_id": oid},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail={"message": "User not found"},
            )

        user = await users_collection.find_one({"_id": oid})

        return {
            "message": "User updated successfully",
            "data": serialize_user(user),
        }
    
    @staticmethod
    async def delete_user(user_id: str):
        oid = validate_object_id(user_id)

        result = await users_collection.delete_one({"_id": oid})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail={"message": "User not found"},
            )

        # clean up related data
        await user_profiles_collection.delete_many({"user_id": oid})
        # Note: We'll delete courses and quizzes in their respective services

        return None  # 204 No Content