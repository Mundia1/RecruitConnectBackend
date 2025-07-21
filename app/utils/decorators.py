from functools import wraps
from flask import current_app, abort, g, request, jsonify

def rate_limit(limit_string):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip rate limiting for OPTIONS requests
            if request.method == 'OPTIONS':
                return f(*args, **kwargs)
                
            # Skip if limiter is not configured (e.g., during testing)
            if not hasattr(current_app, 'limiter'):
                return f(*args, **kwargs)
                
            # Apply rate limiting
            return current_app.limiter.limit(limit_string)(f)(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        if not getattr(g, 'user', None):
            current_app.logger.warning("Admin access denied: No user in request context")
            abort(403, description="Authentication required")
            
        # Check if user has role attribute
        if not hasattr(g.user, 'role'):
            current_app.logger.warning(f"User {g.user.id} has no role assigned")
            abort(403, description="User role not found")
            
        # Check if user is admin
        if g.user.role != 'admin':
            current_app.logger.warning(f"Admin access denied for user {g.user.id} with role {g.user.role}")
            abort(403, description="Admin access required")
            
        return f(*args, **kwargs)
    return decorated_function