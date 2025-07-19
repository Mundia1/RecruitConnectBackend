from functools import wraps
from flask import current_app, abort, g

def rate_limit(limit_string):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            limiter = current_app.limiter
            return limiter.limit(limit_string)(f)(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(g, 'current_user', None) or g.current_user.role != 'admin':
            abort(403, description="Admin access required")
        return f(*args, **kwargs)
    return decorated_function