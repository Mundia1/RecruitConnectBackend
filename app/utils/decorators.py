from functools import wraps
from flask import current_app

def rate_limit(limit_string):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = current_app.limiter
            return limiter.limit(limit_string)(f)(*args, **kwargs)
        return decorated_function
    return decorator
