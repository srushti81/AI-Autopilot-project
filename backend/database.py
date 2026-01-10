import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not found in .env")

client = MongoClient(
    MONGO_URI,
    tls=True,
    serverSelectionTimeoutMS=5000
)

db = client["ai_autopilot"]
