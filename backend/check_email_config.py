import os
import smtplib
import socket
from dotenv import load_dotenv, find_dotenv

# Load env variables
load_dotenv(find_dotenv())

# Get Credentials
username = os.getenv("MAIL_USERNAME")
password = os.getenv("MAIL_PASSWORD")

print("🔹 Email Configuration Check")
print(f"MAIL_USERNAME: {username}")
print(f"MAIL_PASSWORD: {'*' * len(password) if password else 'NOT SET'}")

if not username or not password:
    print("\n❌ Error: Missing MAIL_USERNAME or MAIL_PASSWORD in .env file.")
    print("Please add these to your .env file or Render environment variables.")
    exit(1)

print("\n🔄 Attempting to connect to Gmail SMTP (smtp.gmail.com:587)...")

try:
    # Set timeout to 10 seconds to prevent hanging
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    server.starttls()
    print("✅ Connected to SMTP server.")
    
    print("🔄 Attempting login...")
    server.login(username, password)
    print("✅ Login SUCCESSFUL!")
    print("\n🎉 Your email credentials are correct.")
    
    server.quit()
    
except socket.timeout:
    print("\n❌ Error: Connection timed out. Check your internet connection or firewall.")
except smtplib.SMTPAuthenticationError:
    print("\n❌ Error: Authentication failed. Check your username and app password.")
    print("Note: You must use an App Password, not your regular Gmail password.")
except Exception as e:
    print(f"\n❌ Error: {e}")
