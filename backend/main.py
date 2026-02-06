from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import logging
import traceback
import os

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel

from config import GROQ_API_KEY
from groq import Groq
import gridfs
import resend

# ✅ LOCAL IMPORTS
from auth.auth_routes import router as auth_router
from auth.auth_dependencies import get_current_user
from history.history_routes import router as history_router
from database import client as mongo_client

# ----------------------------------------------------
# 🔹 ENV
# ----------------------------------------------------
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
MAIL_FROM = os.getenv("MAIL_FROM", "no-reply@resend.dev")

if not RESEND_API_KEY:
    raise RuntimeError("RESEND_API_KEY not set")

resend.api_key = RESEND_API_KEY

logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------
# 🔹 DATABASE
# ----------------------------------------------------
db = mongo_client["ai_autopilot"]
fs = gridfs.GridFS(db)
history_collection = db["history"]

# ----------------------------------------------------
# 🔹 AI CLIENT
# ----------------------------------------------------
client = Groq(api_key=GROQ_API_KEY)

# ----------------------------------------------------
# 🔹 FASTAPI APP
# ----------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-autopilot-project-tdz1.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Status {response.status_code}")
    return response

app.include_router(auth_router)
app.include_router(history_router)

# ----------------------------------------------------
# 🔹 MODELS
# ----------------------------------------------------
class UserRequest(BaseModel):
    command: str
    user_id: Optional[str] = None

# ----------------------------------------------------
# 🔹 HEALTH
# ----------------------------------------------------
@app.get("/")
async def root():
    return {"status": "Backend running 🚀"}

@app.get("/ping")
async def ping():
    mongo_client.admin.command("ping")
    return {"db": "connected"}

# ----------------------------------------------------
# 🔹 AI
# ----------------------------------------------------
@app.post("/run")
async def run_command(
    request: UserRequest,
    current_user=Depends(get_current_user)
):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": request.command}],
    )

    result = response.choices[0].message.content

    history_collection.insert_one({
        "user_id": current_user["sub"],
        "command": request.command,
        "response": result,
        "created_at": datetime.utcnow(),
    })

    return {"response": result}

# ----------------------------------------------------
# 🔹 SEND EMAIL (RESEND)
# ----------------------------------------------------
@app.post("/send-email")
async def send_email(
    recipient: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    current_user=Depends(get_current_user),
):
    try:
        email = resend.Emails.send({
            "from": MAIL_FROM,
            "to": recipient,
            "subject": subject,
            "html": f"<p>{body}</p>",
        })

        return {"message": "Email sent successfully", "id": email["id"]}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
