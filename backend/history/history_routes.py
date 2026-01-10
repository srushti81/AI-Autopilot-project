from fastapi import APIRouter
from backend.database import client as mongo_client
from bson import ObjectId

router = APIRouter(
    prefix="/history",
    tags=["History"]
)

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
