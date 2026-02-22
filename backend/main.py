from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import logging
import traceback
import os
import base64

from fastapi import FastAPI, Form, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel

from groq import Groq
import resend
import gridfs

# ✅ LOCAL IMPORTS
from auth.auth_routes import router as auth_router
from auth.auth_dependencies import get_current_user
from history.history_routes import router as history_router
from database import client as mongo_client
from config import GROQ_API_KEY

# ----------------------------------------------------
# 🔹 ENV SETUP
# ----------------------------------------------------
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Test sender (works without domain verification)
MAIL_FROM_RESEND = "onboarding@resend.dev"

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
else:
    logging.warning("⚠️ RESEND_API_KEY not set. Email functionality disabled.")

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
    allow_origins=["*"],  # You can restrict later
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
# 🔹 AI COMMAND
# ----------------------------------------------------
@app.post("/run")
async def run_command(
    request: UserRequest,
    current_user=Depends(get_current_user)
):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="AI API key not configured")

    try:
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

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

# ----------------------------------------------------
# 🔹 SEND EMAIL (RESEND API)
# ----------------------------------------------------
@app.post("/send-email")
async def send_email(
    recipient: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    current_user=Depends(get_current_user),
    attachments: List[UploadFile] = File(None),
):
    try:
        if not RESEND_API_KEY:
            raise HTTPException(status_code=500, detail="Resend API key not configured")

        attachment_list = []
        if attachments:
            for attachment in attachments:
                file_content = await attachment.read()
                attachment_list.append({
                    "filename": attachment.filename,
                    "content": base64.b64encode(file_content).decode(),
                })

        response = resend.Emails.send({
            "from": MAIL_FROM_RESEND,
            "to": recipient,
            "subject": subject,
            "text": body,
            "attachments": attachment_list
        })

        logging.info(f"✅ Email sent via Resend: {response}")

        return {"message": "Email sent successfully via Resend"}

    except Exception as e:
        logging.error(f"❌ RESEND ERROR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
