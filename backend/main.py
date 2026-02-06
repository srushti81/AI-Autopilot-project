from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import logging
import os
import traceback

from pydantic import BaseModel
from groq import Groq
import gridfs
from database import client as mongo_client

from auth.auth_routes import router as auth_router
from auth.auth_dependencies import get_current_user
from history.history_routes import router as history_router

import resend

# ----------------------------------------------------
# 🔹 ENV
# ----------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

resend.api_key = RESEND_API_KEY

logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------
# 🔹 DB
# ----------------------------------------------------
db = mongo_client["ai_autopilot"]
fs = gridfs.GridFS(db)
history_collection = db["history"]

# ----------------------------------------------------
# 🔹 AI CLIENT
# ----------------------------------------------------
client = Groq(api_key=GROQ_API_KEY)

# ----------------------------------------------------
# 🔹 APP
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
# 🔹 LOGGING
# ----------------------------------------------------
@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response {response.status_code}")
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
    return {"status": "ok"}

# ----------------------------------------------------
# 🔹 AI RUN
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
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": recipient,
            "subject": subject,
            "html": f"<p>{body}</p>",
        })

        return {
            "message": "Email sent successfully",
            "resend_id": response["id"]
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
