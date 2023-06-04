import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.mail import send_mail

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_SENDER = os.getenv("SMTP_SENDER")

def send_email(recipient_email, subject, message):
    try:
        # Create a multipart message object
        msg = MIMEMultipart()
        msg["From"] = SMTP_SENDER
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Attach the message to the MIMEMultipart object
        msg.attach(MIMEText(message, "plain"))

        # Connect to the SMTP server provided by your hosting provider
        smtp_server = SMTP_SERVER  # Update this with your SMTP server details
        smtp_port = SMTP_PORT  # Update this with your SMTP server port
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Login to your email account
        server.login(SMTP_SENDER, SMTP_PASSWORD)

        # Send the email
        server.sendmail(SMTP_SENDER, recipient_email, msg.as_string())
        print("Email sent successfully!")
        
    except Exception as e:
        print("An error occurred while sending the email:")
        print(str(e))
    finally:
        # Clean up
        server.quit()

    return True


def send_another_email():
    subject = 'welcome to GFG world'
    message = f'Hi Swift, thank you for registering in geeksforgeeks.'
    email_from = SMTP_SENDER
    recipient_list = ["charlestontaylor09@gmail.com", ]
    
    return send_mail(subject, message, email_from, recipient_list)
    
    