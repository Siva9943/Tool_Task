import re
import pandas as pd
from core.models import *
data = Product_info.objects.all()

def row_validate(row, row_number):
    errors = []

    product_code = row.get("product_code")
    if pd.isna(product_code) or str(product_code).strip() == "":
        errors.append(f"Row {row_number}: Product Code is required.")
    else:
        code = str(product_code).strip()
        if not re.match(r"^P\d+$", code):
            errors.append(f"Row {row_number}: Product Code must be like P001.")
        elif len(code) > 20:
            errors.append(f"Row {row_number}: Product Code cannot exceed 20 characters.")
        else:
            if Product_info.objects.filter(product_code=product_code).exists():
                errors.append(f"Row {row_number}: Product Code already exists.")

    product_name = row.get("product_name")
    if pd.isna(product_name) or str(product_name).strip() == "":
        errors.append(f"Row {row_number}: Product Name is required.")
        
    elif len(str(product_name).strip()) > 40:
        errors.append(f"Row {row_number}: Product Name cannot exceed 40 characters.")

    description = row.get("description")
    if pd.isna(description) or str(description).strip() == "":
        errors.append(f"Row {row_number}: Description is required.")
    
    item_category = row.get("item_category")
    if pd.isna(item_category) or str(item_category).strip() == "":
        errors.append(f"Row {row_number}: Item Category is required.")
    elif len(str(item_category).strip()) > 20 and re.match(r"^a-zA-Z"):
        errors.append(f"Row {row_number}: Item Category cannot exceed 20 characters.")
    

    cost = None
    selling = None

    try:
        cost = float(row["cost_price"])
        if cost < 0:
            errors.append(f"Row {row_number}: Cost Price cannot be negative.")
    except (TypeError, ValueError):
        errors.append(f"Row {row_number}: Cost Price must be numeric.")

    try:
        selling = float(row["selling_price"])
        if selling < 0:
            errors.append(f"Row {row_number}: Selling Price cannot be negative.")
    except (TypeError, ValueError):
        errors.append(f"Row {row_number}: Selling Price must be numeric.")

    if cost is not None and selling is not None and selling < cost:
        errors.append(f"Row {row_number}: Selling Price must be greater than or equal to Cost Price.")
    
    try:
        quantity = int(row["quantity"])
        if quantity < 0:
            errors.append(f"Row {row_number}: Quantity cannot be negative.")
    except (TypeError, ValueError):
        errors.append(f"Row {row_number}: Quantity must be an integer.")
   
    stock = row.get("stock")
    if str(stock).strip().lower() not in ["true", "false", "1", "0", "yes", "no"]:
        errors.append(f"Row {row_number}: Stock must be True or False.")

    return errors