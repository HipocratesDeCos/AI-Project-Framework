"""Spanish presentation helpers; canonical values and identities stay unchanged."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def number_text(value, minimum_decimals=0):
    if value is None or isinstance(value, bool) or str(value).strip() == '':
        return 'Sin datos'
    try:
        number = Decimal(str(value))
        if not number.is_finite():
            return 'Sin datos'
        text = format(number, 'f')
    except (InvalidOperation, ValueError):
        return str(value)
    integer, _, fraction = text.partition('.')
    sign = '-' if integer.startswith('-') else ''
    digits = integer.lstrip('-')
    groups = []
    while digits:
        groups.insert(0, digits[-3:])
        digits = digits[:-3]
    fraction = fraction.ljust(minimum_decimals, '0')
    return sign + '.'.join(groups) + (',' + fraction if fraction else '')


def date_text(value):
    if value is None or str(value).strip() == '':
        return 'Sin fecha'
    text = str(value)
    try:
        if len(text) == 10:
            return date.fromisoformat(text).strftime('%d/%m/%Y')
        instant = datetime.fromisoformat(text.replace('Z', '+00:00'))
        return instant.strftime('%d/%m/%Y %H:%M:%S') + (' ' + instant.strftime('%z') if instant.tzinfo else '')
    except ValueError:
        return text


def supplier_details(supplier):
    def first(*keys):
        for key in keys:
            value = supplier.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None
    return dict(supplier_id=supplier.get('supplier_id'),
                legal_name=first('legal_name'),
                contact_name=first('contact_name', 'contact_person'),
                delivery_location=first('delivery_location', 'delivery_address'))
