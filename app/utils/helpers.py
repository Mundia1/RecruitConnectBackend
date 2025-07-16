from datetime import datetime

def format_datetime(dt):
     
    return dt.isoformat() if isinstance(dt, datetime) else None

def parse_int(value, default=0):
     
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
