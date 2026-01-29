import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content("Test email from Python")
msg["Subject"] = "SMTP Test"
msg["From"] = "YOUR_EMAIL@gmail.com"
msg["To"] = "RECEIVER_EMAIL@gmail.com"

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(
    "srushtipatil015@gmail.com",
    "ynovkajwrxsvhsqy"
)
server.send_message(msg)
server.quit()

print("Email sent")
