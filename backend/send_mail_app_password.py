import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = os.getenv("MAIL_USERNAME")
APP_PASSWORD = os.getenv("MAIL_PASSWORD")

def send_email(subject, message, to_email):
    try:
        # Create the email
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        # Connect to Gmail
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)

        # Send email
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()

        print("Email sent successfully!")

    except Exception as e:
        print("Error sending email:", e)


# Test Function
if __name__ == "__main__":
    send_email(
        "Test Email (App Password)",
        "This is a test email sent via App Password!",
        "yourfriend@gmail.com"
    )
