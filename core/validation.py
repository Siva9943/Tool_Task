import datetime
import re

EXPECTED_COLUMNS = [
    'product code*',
    'product name*',
    'description',
    'item category*',
    'cost price*',
    'selling price*',
    'quantity*',
    'expire date*',
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
    'product code*': 'product_code',
    'product name*': 'product_name',
    'description': 'description',
    'item category*': 'item_category',
    'cost price*': 'cost_price',
    'selling price*': 'selling_price',
    'quantity*': 'quantity',
    'expire date*': 'expire_date',
}

DATE_FORMAT = '%d-%m-%Y'


def validate_template(actual_columns):
    actual = [str(col).strip() for col in actual_columns]
    expected = EXPECTED_COLUMNS

    missing = [col for col in expected if col not in actual]
    print(missing, "hii this is missing column")
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
    print(value, "demo")

    if value is None:
        return None

    text = str(value).split()[0]  

    try:
        return datetime.datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        errors.append("Expire Date must be in YYYY-MM-DD format")
        return None


def validate_row(row, seen_codes, seen_names, existing_codes, existing_names):
    errors = []

    for field in REQUIRED_FIELDS:
        value = row.get(field)
        if clean_str(value) == '':
            errors.append(f'{field.replace("_", " ").title()} is required')

    product_code = clean_str(row.get('product_code'))
    product_name = clean_str(row.get('product_name'))
    description = clean_str(row.get('description'))
    item_category = clean_str(row.get('item_category'))

    if product_code and len(product_code) > 20:
        errors.append('Product Code must be at most 20 characters')

    if product_name and len(product_name) > 40:
        errors.append('Product Name must be at most 40 characters')

    if item_category and len(item_category) > 20:
        errors.append('Item Category must be at most 20 characters')

    cost_price = parse_decimal(row.get('cost_price'), 'Cost Price', errors)
    print(cost_price,'this is cost')
    selling_price = parse_decimal(row.get('selling_price'), 'Selling Price', errors)
    print(selling_price,'this is selling')
    quantity = parse_int(row.get('quantity'), 'Quantity', errors)
    print(quantity,"this is quantity")
    expire_date = parse_date(row.get('expire_date'), errors)
    print(expire_date,"demodsf aiva")
    print(cost_price,"there is date")

    if cost_price is not None and cost_price < 0:
        errors.append('Cost Price must be >= 0')

    if selling_price is not None and selling_price < 0:
        errors.append('Selling Price must be >= 0')

    if quantity is not None and quantity < 0:
        errors.append('Quantity must be >= 0')

    if cost_price is not None and selling_price is not None and selling_price <= cost_price:
        errors.append('Selling Price must be greater than Cost Price')

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
