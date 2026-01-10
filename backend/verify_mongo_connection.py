
import os
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load env from the same directory as main.py would
# Assuming this script is running from the workspace root or I need to point to backend/.env
# The user's backend is in c:\Users\srush\OneDrive\Desktop\AI-Autopilot\backend
# I will run this script in that directory.

env_path = 'c:\\Users\\srush\\OneDrive\\Desktop\\AI-Autopilot\\backend\\.env'
load_dotenv(dotenv_path=env_path)

async def check_mongo():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("MONGODB_URI not found in .env")
        return

    print("MONGODB_URI found.")
    
    # Test connection
    try:
        client = AsyncIOMotorClient(uri)
        # The is_master command is cheap and does not require auth usually, 
        # but ping is better for strict connection check.
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(check_mongo())
