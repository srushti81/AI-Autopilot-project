from fastapi import APIRouter, HTTPException
from models.user_model import UserCreate, UserLogin
from database import db
from auth.simple_auth_utils import hash_password, verify_password
from auth.auth_utils import create_access_token
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup")
def signup(user: UserCreate):
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    inserted = db.users.insert_one({
        "email": user.email,
        "password": hash_password(user.password),
        "created_at": datetime.utcnow()
    })

    user_id = str(inserted.inserted_id)
    token = create_access_token({"sub": user_id, "email": user.email})
    return {
        "message": "Signup successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": user.email}
    }


@router.post("/login")
def login(user: UserLogin):
    db_user = db.users.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = str(db_user["_id"])
    token = create_access_token({"sub": user_id, "email": db_user["email"]})
    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": db_user["email"]}
    }
@router.get("/me/{user_id}")
def get_me(user_id: str):
    user = db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["_id"] = str(user["_id"])
    return user
