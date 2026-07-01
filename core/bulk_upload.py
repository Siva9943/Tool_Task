from .models import *
import pandas as pd

def validate_row(row, row_number):
    errors = []

    if pd.isna(row["product_code"]) or str(row["product_code"]).strip() == "":
        errors.append(f"Row {row_number}: Product Code is required.")
    elif len(str(row["product_code"])) > 20:
        errors.append(f"Row {row_number}: Product Code cannot exceed 20 characters.")

    if pd.isna(row["product_name"]) or str(row["product_name"]).strip() == "":
        errors.append(f"Row {row_number}: Product Name is required.")
    elif len(str(row["product_name"])) > 40:
        errors.append(f"Row {row_number}: Product Name cannot exceed 40 characters.")

    if pd.isna(row["description"]) or str(row["description"]).strip() == "":
        errors.append(f"Row {row_number}: Description is required.")

    if pd.isna(row["item_category"]) or str(row["item_category"]).strip() == "":
        errors.append(f"Row {row_number}: Item Category is required.")
    elif len(str(row["item_category"])) > 20:
        errors.append(f"Row {row_number}: Item Category cannot exceed 20 characters.")
    try:
        cost = float(row["cost_price"])
        if cost < 0:
            errors.append(f"Row {row_number}: Cost Price cannot be negative.")
    except:
        errors.append(f"Row {row_number}: Cost Price must be numeric.")
    try:
        selling = float(row["selling_price"])
        if selling < 0:
            errors.append(f"Row {row_number}: Selling Price cannot be negative.")
    except:
        errors.append(f"Row {row_number}: Selling Price must be numeric.")
    if "cost" in locals() and "selling" in locals():
        if selling < cost:
            errors.append(f"Row {row_number}: Selling Price must be greater than or equal to Cost Price.")
    try:
        quantity = int(row["quantity"])
        if quantity < 0:
            errors.append(f"Row {row_number}: Quantity cannot be negative.")
    except:
        errors.append(f"Row {row_number}: Quantity must be an integer.")
    stock = row["stock"]
    if str(stock).lower() not in ["true", "false", "1", "0", "yes", "no"]:
        errors.append(f"Row {row_number}: Stock must be True or False.")

    return errors
