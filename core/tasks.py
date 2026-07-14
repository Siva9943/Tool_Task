import traceback
from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from io import BytesIO
import pandas as pd
import logging
from email_ops.utils.email_template import EMAIL_BUILDERS
from .models import Email_DB
from email_ops.send_mail_util import send_mail_gmail
logger = logging.getLogger("products")

# @shared_task
# def send_account_creation_email(user_id,subject,message,to,test_cc):
#     try: 
#         user = User.objects.get(id=user_id)
#         send_mail_gmail(to_email=to,cc_email=test_cc,subject=subject,message=message,)
#         Email_DB.objects.filter(user=user).update(email_status="Sent")
#     except Exception as e:
#         Email_DB.objects.filter(user_id=user_id).update(email_status=f"Failed: {str(e)}")
#         logger.error(
#             f"Account creation email failed: {str(e)}"
#         )
#         raise e


# @shared_task
# def send_error_report_email(invalid_rows, to_email):
#     if not invalid_rows:
#         return

#     try:
#         df = pd.DataFrame(invalid_rows)

#         df = df.rename(columns={
#             "row_number": "Row No",
#             "product_code": "Product Code",
#             "product_name": "Product Name",
#             "description": "Description",
#             "item_category": "Item Category",
#             "cost_price": "Cost Price",
#             "selling_price": "Selling Price",
#             "quantity": "Quantity",
#             "expire_date": "Expire Date",
#             "error_message": "Error Message",
#         })

#         df["Issue Type"] = df["Error Message"].apply(
#             lambda x: (
#                 "Duplicate"
#                 if "already exists" in str(x)
#                 else "Invalid"
#             )
#         )

#         excel_buffer = BytesIO()

#         with pd.ExcelWriter(
#             excel_buffer,
#             engine="openpyxl"
#         ) as writer:
#             df.to_excel(
#                 writer,
#                 index=False,
#                 sheet_name="Validation Errors"
#             )

#         excel_buffer.seek(0)

#         mail = EmailMultiAlternatives(
#             subject="Product Upload Validation Report",
#             body="""
# Hello,

# Your product upload has completed.

# Some rows failed validation.
# Please find the attached Excel report.

# Thanks
#             """,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[to_email],
#         )

#         mail.attach(
#             "validation_report.xlsx",
#             excel_buffer.getvalue(),
#             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         )

#         mail.send()

#     except Exception:
#         logger.exception("Validation report email failed")
#         raise





def deliver_email(email_type, context, to, cc=None, user_id=None):
    try:
        print(to,"this is development email")
        builder = EMAIL_BUILDERS[email_type]
        subject, message, attachment = builder(context)
        files = None
        if attachment:
            files = [(attachment["filename"], attachment["content"], attachment["mimetype"])]
        send_mail_gmail(
            to_email=to,
            cc_email=cc,
            subject=subject,
            message=message,
            attachments=files,
        )
        if user_id:
            Email_DB.objects.filter(user_id=user_id).update(email_status="Sent")

    except Exception as e:
        if user_id:
            Email_DB.objects.filter(user_id=user_id).update(email_status=f"Failed: {str(e)}")
        logger.error(f"[{email_type}] email failed: {e}")
        raise e