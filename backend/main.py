from backend.auth.auth_routes import router as auth_router
from backend.history.history_routes import router as history_router
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
from .database import client as mongo_client
import smtplib
from backend.auth.auth_utils import hash_password
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io
from typing import List
import logging
import uvicorn

logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------
# 🔹 Load Environment Variables
# ----------------------------------------------------
from pathlib import Path
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# 🔹 Import Database (AFTER loading env vars)
try:
    from .database import client as mongo_client
except ImportError:
    from database import client as mongo_client

# ----------------------------------------------------
# 🔹 Initialize Groq Client
# ----------------------------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ----------------------------------------------------
# 🔹 Create FastAPI App
# ----------------------------------------------------
app = FastAPI()
app.include_router(auth_router)
app.include_router(history_router)


# ----------------------------------------------------
# 🔹 CORS (Allow Frontend to Connect)
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

logging.info(f"Email ConnectionConfig: "
             f"MAIL_USERNAME={conf.MAIL_USERNAME}, "
             f"MAIL_FROM={conf.MAIL_FROM}, "
             f"MAIL_PORT={conf.MAIL_PORT}, "
             f"MAIL_SERVER={conf.MAIL_SERVER}, "
             f"MAIL_STARTTLS={conf.MAIL_STARTTLS}, "
             f"MAIL_SSL_TLS={conf.MAIL_SSL_TLS}")

# ----------------------------------------------------
# 🔹 Models
# ----------------------------------------------------

class EmailSchema(BaseModel):
    recipient: str
    subject: str

class EmailRequest(BaseModel):
    to: str
    subject: str
    message: str
    
class UserRequest(BaseModel):
    user_id: str
    command: str


# ----------------------------------------------------
# 🔹 TEST ROUTE
# ----------------------------------------------------
@app.get("/ping")
async def ping():
    return {"message": "Backend is running"}



@app.get("/")
async def root():
    return {
        "status": "ok",
        "endpoints": ["/ping", "/run", "/send-email"],
    }

# ----------------------------------------------------
# 🔹 AI COMMAND ENDPOINT (Groq AI Model)
# ----------------------------------------------------
@app.post("/run")
async def run_command(request: UserRequest):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": request.command}
            ]
        )

        result = response.choices[0].message.content

        # ✅ SAVE TO DATABASE
        mongo_client.ai_autopilot.history.insert_one({
            "user_id": request.user_id,
            "command": request.command,
            "response": result,
            "created_at": datetime.utcnow()
        })

        return {"response": result}

    except Exception as e:
        return {"error": str(e)}


@app.post("/send-email")
async def send_email(
    recipient: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    attachments: List[UploadFile] = File(default=[]),
):
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[recipient],
            body=body,
            subtype="html",
            attachments=attachments
        )

        logging.info(f"Received email request for: {recipient}, Subject: {subject}")
        logging.info(f"Number of attachments received: {len(attachments) if attachments else 0}")

        fm = FastMail(conf)
        try:
            await fm.send_message(message)
            logging.info("Email sent successfully!")
            return {"message": "Email has been sent"}
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return {"error": str(e)}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {"error": str(e)}


