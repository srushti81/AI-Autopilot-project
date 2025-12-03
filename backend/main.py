from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io
from typing import List
import logging

logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------
# 🔹 Load Environment Variables
# ----------------------------------------------------
load_dotenv(dotenv_path='c:\\AI-Autopilot\\backend\\.env')

# ----------------------------------------------------
# 🔹 Initialize Groq Client
# ----------------------------------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ----------------------------------------------------
# 🔹 Create FastAPI App
# ----------------------------------------------------
app = FastAPI()

# ----------------------------------------------------
# 🔹 CORS (Allow Frontend to Connect)
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
class UserRequest(BaseModel):
    command: str

class EmailSchema(BaseModel):
    recipient: str
    subject: str

class EmailRequest(BaseModel):
    to: str
    subject: str
    message: str

# ----------------------------------------------------
# 🔹 TEST ROUTE
# ----------------------------------------------------
@app.get("/ping")
def ping():
    return {"message": "Backend is running!"}

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

