from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import logging
import traceback
import os

from fastapi import FastAPI, Form, Depends, HTTPException, File, UploadFile
from typing import Optional, List
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from groq import Groq
import resend
import gridfs

# ✅ LOCAL IMPORTS
from auth.auth_routes import router as auth_router
from auth.auth_dependencies import get_current_user
from history.history_routes import router as history_router
from database import client as mongo_client
from config import GROQ_API_KEY, MAIL_USERNAME, MAIL_PASSWORD, MAIL_SERVER, MAIL_PORT, MAIL_FROM

# ----------------------------------------------------
# 🔹 ENV SETUP
# ----------------------------------------------------
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# ⚠️ IMPORTANT:
# Test mode sender — DO NOT change until domain is verified
MAIL_FROM_RESEND = "onboarding@resend.dev"

if not RESEND_API_KEY:
    logging.warning("RESEND_API_KEY not set. Email functionality will be disabled.")
else:
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
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:5173",
        "https://ai-autopilot-project-tdz1.vercel.app",
        "https://*.netlify.app", # ✅ Allow all netlify subdomains
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
# 🔹 AI COMMAND
# ----------------------------------------------------
@app.post("/run")
async def run_command(
    request: UserRequest,
    current_user=Depends(get_current_user)
):
    print(f"🔹 Received AI command: {request.command}")
    
    if not GROQ_API_KEY:
        print("❌ Error: GROQ_API_KEY is not set in environment.")
        raise HTTPException(status_code=500, detail="AI API key not configured")

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": request.command}],
        )

        result = response.choices[0].message.content
        print(f"✅ AI Response: {result[:50]}...")

        history_collection.insert_one({
            "user_id": current_user["sub"],
            "command": request.command,
            "response": result,
            "created_at": datetime.utcnow(),
        })

        return {"response": result}

    except Exception as e:
        print(f"❌ AI ERROR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

# ----------------------------------------------------
# 🔹 SEND EMAIL (GMAIL SMTP)
# ----------------------------------------------------
# ----------------------------------------------------
# 🔹 SEND EMAIL (GMAIL SMTP)
# ----------------------------------------------------
@app.post("/send-email")
async def send_email(
    recipient: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    attachments: List[UploadFile] = File(None),
    current_user=Depends(get_current_user),
):
    try:
        if not MAIL_USERNAME or not MAIL_PASSWORD:
            raise HTTPException(status_code=500, detail="Mail credentials not configured")

        msg = MIMEMultipart()
        msg["From"] = MAIL_FROM or MAIL_USERNAME
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        if attachments:
            for attachment in attachments:
                part = MIMEBase("application", "octet-stream")
                content = await attachment.read()
                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={attachment.filename}",
                )
                msg.attach(part)

        # ✅ Correct SMTP block (INSIDE try)
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, recipient, msg.as_string())
        server.quit()

        return {"message": "Email sent successfully via Gmail"}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"SMTP Error: {str(e)}")
