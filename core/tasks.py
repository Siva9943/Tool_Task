from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_validation_email(email, body):
    send_mail(
        subject="Upload Validation Report",
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=body,
    )


def build_error_table(errors):
    rows = ""

    for error in errors:
        if ":" in error:
            left, right = error.split(":", 1)
            row_num = left.replace("Row", "").strip()
            message = right.strip()
        else:
            row_num = "-"
            message = error

        rows += f"""
        <tr>
            <td style="padding:10px; border:1px solid #ddd; text-align:center;">
                {row_num}
            </td>
            <td style="padding:10px; border:1px solid #ddd; color:#b30000;">
                {message}
            </td>
        </tr>
        """

    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;background:#f9f9f9;padding:20px;">
        <div style="max-width:700px;margin:auto;background:white;padding:20px;border-radius:10px;">
            <h2 style="color:#d9534f;text-align:center;">
                Validation Error Report
            </h2>

            <table style="width:100%;border-collapse:collapse;">
                <thead>
                    <tr>
                        <th>Row</th>
                        <th>Error Message</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """