from pymongo import MongoClient
from dotenv import load_dotenv
import os
import gridfs
import certifi

from config import MONGO_URI

if not MONGO_URI:
    raise RuntimeError("MongoDB URI not configured. Set MONGO_URI in .env")

# 🔹 Create Mongo client (Atlas-safe)
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

# 🔹 Use ONE database only
db = client["ai_autopilot"]

# 🔹 GridFS for attachments
fs = gridfs.GridFS(db)
