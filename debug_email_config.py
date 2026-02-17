import os
import smtplib
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

user = os.getenv("MAIL_USERNAME")
password = os.getenv("MAIL_PASSWORD")

print(f"MAIL_USERNAME: {user}")
if password:
    print(f"MAIL_PASSWORD length: {len(password)}")
else:
    print("MAIL_PASSWORD: None")

if not user or not password:
    print("Missing credentials")
    exit(1)

print("Attempting to connect to smtp.gmail.com:587...")
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    print("Logging in...")
    try:
        server.login(user, password)
        print("Login successful!")
    except Exception as e:
        print(f"Login failed: {e}")
    finally:
        server.quit()
except Exception as e:
    print(f"Connection failed: {e}")
