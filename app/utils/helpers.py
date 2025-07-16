from datetime import datetime

def format_datetime(dt):
     
    return dt.isoformat() if isinstance(dt, datetime) else None

def parse_int(value, default=0):
     
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
def is_valid_email(email):
    
    if not isinstance(email, str):
        return False
    return "@" in email and "." in email.split("@")[-1]
