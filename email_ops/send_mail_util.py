from dotenv import load_dotenv
load_dotenv()
import os

from django.conf import settings
from django.core.mail import EmailMessage, get_connection


def send_mail_gmail(to_email, cc_email, subject, message, attachments=None):
    try:
        print("Creating SMTP connection...")
        connection = get_connection(
            host="smtp.gmail.com",
            port=587,
            username=os.getenv("EMAIL_HOST_USER"),
            password=os.getenv("EMAIL_HOST_PASSWORD"),
            use_tls=True,
            timeout=10,
        )
        if isinstance(to_email, str):
            to_email = [to_email]

        if isinstance(cc_email, str):
            cc_email = [cc_email]
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=os.getenv("EMAIL_HOST_USER"),
            to=to_email,
            cc=cc_email or [],
            connection=connection,
        )
        print("HOST:", settings.EMAIL_HOST)
        print("PORT:", settings.EMAIL_PORT)
        print("USER:", settings.EMAIL_HOST_USER)
        print("PASSWORD EXISTS:", bool(settings.EMAIL_HOST_PASSWORD))
        for filename, content, mimetype in attachments or []:
            email.attach(filename, content, mimetype)
        email.send()
       
        return True
    except Exception as e:

        print("Gmail sending failed:", e)
        raise e