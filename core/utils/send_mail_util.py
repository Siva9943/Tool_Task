from dotenv import load_dotenv
from django.core.mail import EmailMessage, get_connection
load_dotenv()
import os


def send_mail_gmail(to_email, cc_email, subject, message):
    connection = get_connection(
        host='smtp.gmail.com',
        port=587,
        username=os.getenv('EMAIL_HOST_USER'),
        password=os.getenv('EMAIL_HOST_PASSWORD'),
        use_tls=True,
    )

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=os.getenv('EMAIL_HOST_USER'),
        to=[to_email],
        cc=[cc_email] if cc_email else [],
        connection=connection,
    )

    email.send()