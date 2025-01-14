from datetime import datetime


def format_date(value, format='%d.%m.%Y'):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value
