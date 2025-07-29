from flask import Flask, g, request, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request  # Add this import
from .extensions import db, migrate, jwt, metrics, cache
from flask_cors import CORS  # Add this import
from .resources import register_resources
from config import config_by_name  # Import the dictionary
from flask_limiter.util import get_remote_address  # Import get_remote_address
from flask_limiter import Limiter  # Import Limiter
import structlog  # Import structlog for logging
from datetime import timedelta
from flask_mail import Mail

mail = Mail()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])  # Pass the class, not a string
    db.init_app(app)
    migrate.init_app(app, db)
    register_resources(app)  # <-- This registers all blueprints
    
    # Initialize JWT
    jwt.init_app(app)
    
    # Configure CORS with specific settings for development
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])  # Allow frontend origin
    
    # Add any additional headers that aren't CORS-related here
    @app.after_request
    def add_security_headers(response):
        # Add security headers if needed
        # response.headers['X-Content-Type-Options'] = 'nosniff'
        # response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    from app.models.user import User

    @app.before_request
    def load_logged_in_user():
        g.user = None
        g.current_user = None  # For backward compatibility
        
        # Skip for OPTIONS requests
        if request.method == 'OPTIONS':
            return
            
        try:
            # Verify the JWT without raising an error if it's missing
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
                
                if user_id:
                    user = db.session.get(User, user_id)
                    if user:
                        g.user = user
                        g.current_user = user  # For backward compatibility
                        current_app.logger.debug(f"Loaded user {user_id} into request context")
                    else:
                        current_app.logger.warning(f"User {user_id} not found in database")
                else:
                    current_app.logger.debug("No user ID in JWT")
            except Exception as jwt_error:
                # Log the JWT error but don't block the request
                current_app.logger.debug(f"JWT verification failed: {str(jwt_error)}")
                
        except Exception as e:
            # Log any other exceptions
            current_app.logger.error(f"Error in load_logged_in_user: {str(e)}", exc_info=True)

    # Initialize rate limiter with metrics
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["100 per minute"],  # Increase this value for dev
    )
    limiter.init_app(app)
    app.limiter = limiter
    
    # Initialize other extensions
    cache.init_app(app)
    mail.init_app(app)  

    # Set JWT access token expiration
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)  # Example: 2 hours

    # Initialize Celery
    from .extensions import celery  # Make sure celery is imported from your extensions module
    celery.conf.update(app.config)

    log = structlog.get_logger()

    # Import the API blueprint
    from app.blueprints.api_v1 import api_v1_bp

    @app.route('/')
    def home():
        return "Welcome to RecruitConnect API"

    # Import and register error handlers
    #from .errors import register_error_handlers  # Make sure this exists in app/errors.py
    #register_error_handlers(app)

    return app

from app.blueprints.api_v1 import api_v1_bp

def register_resources(app):
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

# Example config in app/__init__.py
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your_email@gmail.com'
MAIL_PASSWORD = 'your_app_password'  # Use an App Password, not your Gmail password
MAIL_DEFAULT_SENDER = 'your_email@gmail.com'
