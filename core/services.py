import pandas as pd
from django.db import transaction
from .models import Product_info
from .validation import COLUMN_FIELD_MAP, validate_template, validate_row


def map_row(raw_row):
    mapped = {}
    for column, field_name in COLUMN_FIELD_MAP.items():
        mapped[field_name] = raw_row.get(column)
    return mapped


def process_upload_file(user, uploaded_file):
    file_name = uploaded_file.name

    if file_name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
    elif file_name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file, sheet_name=0, dtype=str, keep_default_na=False, engine='openpyxl')
    else:
        return {
            "success_count": 0,
            "failed_count": 0,
            "products": [],
            "invalid_rows": [],
            "template_error": "Only .csv and .xlsx files are supported.",
        }

    template_errors = validate_template(df.columns)
    if template_errors:
        return {
            "success_count": 0,
            "failed_count": len(df),
            "products": [],
            "invalid_rows": [],
            "template_error": " | ".join(template_errors),
        }

    existing_codes = set(Product_info.objects.values_list('product_code', flat=True))
    existing_names = set(Product_info.objects.values_list('product_name', flat=True))

    seen_codes = set()
    seen_names = set()
    valid_objects = []
    invalid_rows = []

    for idx, raw_row in df.iterrows():
        row_number = idx + 2
        mapped_row = map_row(raw_row)

        cleaned_data, errors = validate_row(
            mapped_row,
            seen_codes,
            seen_names,
            existing_codes,
            existing_names,
        )

        if errors:
            invalid_rows.append({
                "row_number": row_number,
                "product_code": mapped_row.get("product_code", ""),
                "product_name": mapped_row.get("product_name", ""),
                "quantity": mapped_row.get("quantity", ""),
                "expire_date": mapped_row.get("expire_date", ""),
                "error_message": "; ".join(errors),
            })
        else:
            valid_objects.append(Product_info(
                user=user,
                product_code=cleaned_data["product_code"],
                product_name=cleaned_data["product_name"],
                description=cleaned_data["description"],
                item_category=cleaned_data["item_category"],
                cost_price=cleaned_data["cost_price"],
                selling_price=cleaned_data["selling_price"],
                quantity=cleaned_data["quantity"],
                expire_date=cleaned_data["expire_date"],
            ))
        
    if valid_objects:
        with transaction.atomic():
            Product_info.objects.bulk_create(valid_objects, batch_size=500)

    return {
        "success_count": len(valid_objects),
        "failed_count": len(invalid_rows),
        "products": valid_objects,
        "invalid_rows": invalid_rows,
        "template_error": None,
    }