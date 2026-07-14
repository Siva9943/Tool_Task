def build_signup_email(context):
    user = context["user"]  # {"username", "email", "first_name"}
    subject = "Account Creation Successful"
    print("context in build_signup_email:", context)
    message = f"""Hi {user.get('first_name') or user.get('username')},

Your account has been created successfully.

Username: {user.get('username')}
Email: {user.get('email')}

Thank you.
"""
    return subject, message, None


def build_error_report_email(context):

    import pandas as pd
    from io import BytesIO
    print("context in build_error_report_email:", context)
    invalid_rows = context["invalid_rows"]

    df = pd.DataFrame(invalid_rows).rename(columns={
        # "row_number": "Row No",
        "product_code": "Product Code",
        "product_name": "Product Name",
        "description": "Description",
        "item_category": "Item Category",
        "cost_price": "Cost Price",
        "selling_price": "Selling Price",
        "quantity": "Quantity",
        "expire_date": "Expire Date",
        "error_message": "Error Message",
    })
    df["Issue Type"] = df["Error Message"].apply(
        lambda x: "Duplicate" if "already exists" in str(x) else "Invalid"
    )

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Validation Errors")
    buffer.seek(0)

    subject = "Product Upload Validation Report"
    message = """Hello,

Your product upload has completed.

Some rows failed validation.
Please find the attached Excel report.

Thanks
"""
    attachment = {
        "filename": "validation_report.xlsx",
        "content": buffer.getvalue(),
        "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    return subject, message, attachment


def build_notification_email(context):
    print("context in build_notification_email:", context)
    subject = context.get("subject", "Notification")
    message = context.get("message", "")
    return subject, message, None


def build_otp_email(context):
    user = context["user"]  # {"username", "email", "full_name"}
    otp = context["otp"]
    subject = "Your Verification Code"
    message = f"""Hi {user.get('full_name') or user.get('username')},

Your verification code is: {otp}

This code will expire in 10 minutes.

Thank you.
"""
    return subject, message, None


EMAIL_BUILDERS = {
    "signup": build_signup_email,
    "error_report": build_error_report_email,
    "notification": build_notification_email,
    "otp": build_otp_email,
}