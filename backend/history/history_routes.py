from fastapi import APIRouter
from database import client as mongo_client
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(
    prefix="/history",
    tags=["History"]
)

# -----------------------------
# 🔹 Pydantic Model
# -----------------------------
class HistoryCreate(BaseModel):
    user_id: str
    command: str
    response: str

# -----------------------------
# 🔹 SAVE history
# -----------------------------
@router.post("/save")
async def save_history(data: HistoryCreate):
    record = {
        "user_id": data.user_id,
        "command": data.command,
        "response": data.response,
        "created_at": datetime.utcnow()
    }

    mongo_client.ai_autopilot.history.insert_one(record)

    return {"message": "History saved"}

# -----------------------------
# 🔹 GET history (your existing code)
# -----------------------------
@router.get("/{user_id}")
async def get_user_history(user_id: str):
    history = mongo_client.ai_autopilot.history.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(10)

    results = []
    for item in history:
        item["_id"] = str(item["_id"])
        results.append(item)

    return {
        "user_id": user_id,
        "history": results
    }
