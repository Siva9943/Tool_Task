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
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
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
            from_email=settings.EMAIL_HOST_USER,
            to=to_email,
            cc=cc_email or [],
            connection=connection,
        )


        for filename, content, mimetype in attachments or []:
            email.attach(filename, content, mimetype)

        email.send(fail_silently=False)
        print("Email sent successfully to:", to_email)
        return True

    except Exception as e:
        print("Gmail sending failed:", e)
        raise