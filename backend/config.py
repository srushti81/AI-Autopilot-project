import os
from dotenv import load_dotenv, find_dotenv

# 🔹 LOAD ENV (Centralized)
load_dotenv(find_dotenv())

# ----------------------------------------------------
# 🔹 JWT CONFIG
# ----------------------------------------------------
JWT_SECRET = (os.getenv("JWT_SECRET") or os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or "dev-secret").strip()
JWT_ALGORITHM = (os.getenv("JWT_ALGORITHM") or os.getenv("ALGORITHM") or "HS256").strip()
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES") or os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 60)

# ----------------------------------------------------
# 🔹 DATABASE CONFIG
# ----------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI")

# ----------------------------------------------------
# 🔹 MAIL CONFIG
# ----------------------------------------------------
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")

# ----------------------------------------------------
# 🔹 AI CONFIG
# ----------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
