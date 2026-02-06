from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import logging
import smtplib
import traceback

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel

from config import GROQ_API_KEY, MAIL_USERNAME, MAIL_PASSWORD
from groq import Groq
import gridfs

# LOCAL IMPORTS
from auth.auth_routes import router as auth_router
from auth.auth_dependencies import get_current_user
from history.history_routes import router as history_router
from database import client as mongo_client

# ----------------------------------------------------
# LOGGING
# ----------------------------------------------------
logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------
# DATABASE
# ----------------------------------------------------
db = mongo_client["ai_autopilot"]
fs = gridfs.GridFS(db)
history_collection = db["history"]

# ----------------------------------------------------
# AI CLIENT
# ----------------------------------------------------
client = Groq(api_key=GROQ_API_KEY)

# ----------------------------------------------------
# FASTAPI APP
# ----------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-autopilot-project-tdz1.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# REQUEST LOGGER
# ----------------------------------------------------
@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response {response.status_code}")
    return response

# ----------------------------------------------------
# ROUTERS
# ----------------------------------------------------
app.include_router(auth_router)
app.include_router(history_router)

# ----------------------------------------------------
# MODELS
# ----------------------------------------------------
class UserRequest(BaseModel):
    command: str
    user_id: Optional[str] = None

# ----------------------------------------------------
# HEALTH
# ----------------------------------------------------
@app.get("/")
async def root():
    return {"status": "Backend running 🚀"}

@app.get("/ping")
async def ping():
    mongo_client.admin.command("ping")
    return {"status": "ok", "db": "connected"}

# ----------------------------------------------------
# AI COMMAND
# ----------------------------------------------------
@app.post("/run")
async def run_command(
    request: UserRequest,
    current_user=Depends(get_current_user),
):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": request.command}],
        )

        result = response.choices[0].message.content
        user_id = request.user_id or current_user.get("sub")

        history_collection.insert_one({
            "user_id": user_id,
            "command": request.command,
            "response": result,
            "created_at": datetime.utcnow(),
        })

        return {"response": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------
# SMTP (SYNC FUNCTION)
# ----------------------------------------------------
def send_email_sync(msg: MIMEMultipart):
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
    server.starttls()
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

# ----------------------------------------------------
# SEND EMAIL (NO AUTH – IMPORTANT)
# ----------------------------------------------------
@app.post("/send-email")
async def send_email(
    recipient: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    attachments: List[UploadFile] = File(default=[]),
):
    try:
        msg = MIMEMultipart()
        msg["From"] = MAIL_USERNAME
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        for file in attachments:
            data = await file.read()
            part = MIMEBase("application", "octet-stream")
            part.set_payload(data)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{file.filename}"'
            )
            msg.attach(part)

        # ✅ IMPORTANT: Run SMTP in threadpool
        await run_in_threadpool(send_email_sync, msg)

        return {"message": "Email sent successfully"}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
