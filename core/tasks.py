from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from django.contrib.auth.models import User
from core.utils.send_mail_util import *
import csv
import io
import logging
from django.core.mail import EmailMessage

logger = logging.getLogger('products')


@shared_task
def send_account_creation_email(user_id):
    try:
        user = User.objects.get(id=user_id)

        subject = "Account Creation Successful"

        message = f"""
            Hi {user.first_name or user.username},
            Your account has been created successfully.
            Username: {user.username}
            Email: {user.email}
                Thank you.  
            """
        send_mail_gmail(
            to_email=user.email,
            cc_email=None,
            subject=subject,
            message=message,
        )

        Email_DB.objects.filter(user=user).update(
            email_status="Sent"
        )

    except Exception as e:
        Email_DB.objects.filter(user_id=user_id).update(
            email_status=f"Failed: {str(e)}"
        )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_error_report_email(self, batch_id):
    try:
        batch = UploadBatch.objects.select_related('user').get(id=batch_id)
    except UploadBatch.DoesNotExist:
        logger.error('send_error_report_email: batch %s not found', batch_id)
        return

    invalid_rows = batch.invalid_rows.all()
    if not invalid_rows.exists():
        logger.info('send_error_report_email: no invalid rows for batch %s, skipping', batch_id)
        return

    recipient = batch.user.email
    if not recipient:
        logger.warning('send_error_report_email: user %s has no email, skipping', batch.user)
        return

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(['Row Number', 'Product Code', 'Product Name', 'Quantity', 'Expire Date', 'Error'])
    for row in invalid_rows:
        writer.writerow([
            row.row_number, row.product_code, row.product_name,
            row.quantity, row.expire_date, row.error_message,
        ])

    try:
        email = EmailMessage(
            subject='Product Upload Error Report',
            body=(
                'Please find attached the list of rows that failed validation '
                f'during upload of "{batch.file_name}".\n\n'
                f'Total rows: {batch.total_rows}\n'
                f'Successfully uploaded: {batch.success_count}\n'
                f'Failed validation: {batch.failed_count}\n'
            ),
            to=[recipient],
        )
        email.attach(
            f'invalid_rows_batch_{batch.id}.csv',
            csv_buffer.getvalue(),
            'text/csv',
        )
        email.send(fail_silently=False)

        batch.error_report_sent = True
        batch.save(update_fields=['error_report_sent'])
        logger.info('Error report emailed to %s for batch %s', recipient, batch_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception('Failed to send error report email for batch %s', batch_id)
        raise self.retry(exc=exc)












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