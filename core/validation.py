import datetime
import re

EXPECTED_COLUMNS = [
    'Product code*',
    'Product name*',
    'Description',
    'Item category',
    'Cost price',
    'Selling price*',
    'Quantity*',
    'Expire date(YYYY-MM-DD)',
]   

REQUIRED_FIELDS = [
    'product_code',
    'product_name',
    'description',
    'item_category',
    'cost_price',
    'selling_price',
    'quantity',
    'expire_date',
]
COLUMN_FIELD_MAP = {
    'Product code*': 'product_code',
    'Product name*': 'product_name',
    'Description': 'description',
    'Item category': 'item_category',
    'Cost price': 'cost_price',
    'Selling price*': 'selling_price',
    'Quantity*': 'quantity',
    'Expire date(YYYY-MM-DD)': 'expire_date',
}

DATE_FORMAT = '%Y-%m-%d'


def validate_template(actual_columns):
    actual = [str(col).strip() for col in actual_columns]
    expected = EXPECTED_COLUMNS
    missing = [col for col in expected if col not in actual]
    extra = [col for col in actual if col not in expected]
    errors = []
    if missing:
        errors.append(f"Missing required column(s): {', '.join(missing)}")
    if extra:
        errors.append(f"Unexpected extra column(s): {', '.join(extra)}")
    if not missing and not extra and actual != expected:
        errors.append("Column order does not match the required template order.")
    return errors


def clean_str(value):
    if value is None:
        return ''
    text = str(value).strip()
    return '' if text.lower() == 'nan' else text


def parse_decimal(value, label, errors):
    text = clean_str(value)
    if text == '':
        return None
    try:
        return round(float(text), 2)
    except (TypeError, ValueError):
        errors.append(f'{label} must be a valid decimal number')
        return None


def parse_int(value, label, errors):
    text = clean_str(value)
    if text == '':
        return None
    if not re.fullmatch(r'-?\d+', text):
        errors.append(f'{label} must be a whole integer')
        return None
    return int(text)


def parse_date(value, errors):
    if value is None or value == '':
        return None
    try:
        if isinstance(value, (datetime.datetime, datetime.date)):
            return value.date() if isinstance(value, datetime.datetime) else value
        text = str(value).strip().split()[0]

        return datetime.datetime.strptime(
            text,
            DATE_FORMAT
        ).date()

    except (ValueError, TypeError):
        errors.append("Expire Date must be in YYYY-MM-DD format")
        return None
    
def validate_row(row, seen_codes, seen_names, existing_codes, existing_names):
    errors = []

    product_code = clean_str(row.get('product_code'))
    product_name = clean_str(row.get('product_name'))
    description = clean_str(row.get('description'))
    item_category = clean_str(row.get('item_category'))

    # Required fields
    required_map = {
        'product_code': 'Product Code',
        'product_name': 'Product Name',
        'selling_price': 'Selling Price',
        'quantity': 'Quantity',
    }

    for field, label in required_map.items():
        if clean_str(row.get(field)) == '':
            errors.append(f'{label} is required')
    if product_code:
        if len(product_code) > 20:
            errors.append('Product Code must be at most 20 characters')
        if not re.fullmatch(r'P\d{4,}', product_code):
            errors.append('Product Code must be in Start "P"/4 digits above' )
    if product_name:
        if len(product_name)>50:
            errors.append('Product Name must below 50 characters')
        elif not re.fullmatch(r"^[A-Za-z][A-Za-z0-9\s\-\(\)\.\/]*$", product_name):
            errors.append('Product Name must contain only letters')
    if item_category and len(item_category) > 50:
        errors.append('Item Category must be at most 50 characters')

    if description and len(description) > 150:
        errors.append('Description must be at most 150 characters')

    quantity = parse_int(row.get('quantity'), 'Quantity', errors)
    if quantity is not None:
        if quantity < 0:
            errors.append('Quantity must be greater than or equal to 0')
        elif quantity > 5000:
            errors.append('Quantity must not exceed 5000')

    selling_price = parse_decimal(row.get('selling_price'), 'Selling Price', errors)
    if selling_price is not None:
        if selling_price < 0:
            errors.append('Selling Price must be greater than or equal to 0')

    cost_price = parse_decimal(row.get('cost_price'), 'Cost Price', errors)
    if cost_price is not None:
        if cost_price < 0:
            errors.append('Cost Price must be greater than or equal to 0')
        elif cost_price > 10000000:
            errors.append('Cost Price must not exceed ₹1,00,00,000')

    expire_date = parse_date(row.get('expire_date'), errors)
    if expire_date is not None and expire_date < datetime.date.today():
        errors.append('Expire Date must not be in the past')

    if product_code and product_code in existing_codes:
        errors.append(f'Product Code "{product_code}" already exists in the database')

    if product_name and product_name in existing_names:
        errors.append(f'Product Name "{product_name}" already exists in the database')

    if product_code:
        if product_code in seen_codes:
            errors.append(f'Duplicate Product Code "{product_code}" within the uploaded file')
        else:
            seen_codes.add(product_code)

    if product_name:
        if product_name in seen_names:
            errors.append(f'Duplicate Product Name "{product_name}" within the uploaded file')
        else:
            seen_names.add(product_name)

    cleaned_data = {
        'product_code': product_code,
        'product_name': product_name,
        'description': description,
        'item_category': item_category,
        'cost_price': cost_price,
        'selling_price': selling_price,
        'quantity': quantity,
        'expire_date': expire_date,
    }

    return cleaned_data, errors
