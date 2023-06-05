import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# SMTP server configuration
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")  # Replace with the appropriate port number
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_email(recipient_email, subject, message):
    try:
        # Create a multipart message
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Add message body
        msg.attach(MIMEText(message, "plain"))

        # Create SMTP server connection
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            # server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)

            # Send email
            server.send_message(msg)

    except Exception as e:
        print("An error occurred while sending the email:", str(e))

    return True
