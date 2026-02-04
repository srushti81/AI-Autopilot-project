from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from config import GROQ_API_KEY, MAIL_USERNAME, MAIL_PASSWORD

from groq import Groq
import gridfs

# ✅ LOCAL IMPORTS (NO "backend." PREFIX)
from auth.auth_routes import router as auth_router
from auth.auth_dependencies import get_current_user
from history.history_routes import router as history_router
from database import client as mongo_client

# ----------------------------------------------------
# 🔹 ENV SETUP
# ----------------------------------------------------
# Moved to top

logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------
# 🔹 DATABASE SETUP
# ----------------------------------------------------
db = mongo_client["ai_autopilot"]
fs = gridfs.GridFS(db)
emails_collection = db["emails"]
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
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 🔹 Logging Middleware for Debugging
@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response

app.include_router(auth_router)
app.include_router(history_router)

# ----------------------------------------------------
# 🔹 CORS
# ----------------------------------------------------


# ----------------------------------------------------
# 🔹 MODELS
# ----------------------------------------------------
class UserRequest(BaseModel):
    command: str
    user_id: Optional[str] = None


# ----------------------------------------------------
# 🔹 HEALTH CHECK
# ----------------------------------------------------
@app.get("/ping")
async def ping():
    try:
        mongo_client.admin.command("ping")
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/")
async def root():
    return {"status": "Backend running 🚀"}

@app.get("/debug-auth")
async def debug_auth():
    from auth.auth_dependencies import JWT_SECRET as dep_secret
    from auth.auth_utils import JWT_SECRET as utils_secret
    import os
    env_secret = os.getenv("JWT_SECRET", "NOT_SET").strip()
    return {
        "dep_secret": f"{dep_secret[:2]}...{dep_secret[-2:]}" if len(dep_secret) > 2 else dep_secret,
        "utils_secret": f"{utils_secret[:2]}...{utils_secret[-2:]}" if len(utils_secret) > 2 else utils_secret,
        "env_secret": f"{env_secret[:2]}...{env_secret[-2:]}" if len(env_secret) > 2 else env_secret,
        "all_match": dep_secret == utils_secret == env_secret,
        "len_dep": len(dep_secret),
        "len_utils": len(utils_secret),
        "len_env": len(env_secret)
    }


# ----------------------------------------------------
# 🔹 AI COMMAND ENDPOINT
# ----------------------------------------------------
@app.post("/run")
async def run_command(
    request: UserRequest,
    current_user=Depends(get_current_user)
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
# 🔹 SEND EMAIL
# ----------------------------------------------------
@app.post("/send-email")
async def send_email(
    recipient: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    attachments: List[UploadFile] = File(default=[]),
    current_user=Depends(get_current_user),
):
    try:
        msg = MIMEMultipart()
        msg["From"] = MAIL_USERNAME
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        for file in attachments:
            file_bytes = await file.read()
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file_bytes)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{file.filename}"'
            )
            msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(
            MAIL_USERNAME,
            MAIL_PASSWORD,
        )
        server.send_message(msg)
        server.quit()

        return {"message": "Email sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
