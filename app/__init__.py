from flask import Flask, g, request, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from .extensions import db, migrate, jwt, metrics, cache, mail
from flask_cors import CORS
from config import config_by_name
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
import structlog

# Initialize extensions
cors = CORS()



def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])  # Load config

    app.url_map.strict_slashes = False  # Disable strict slashes for all routes

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)

    # Configure CORS
    cors.init_app(app,
                  resources={r"/*": {
                      "origins": [
                          "http://localhost:5173",
                          "http://127.0.0.1:5173"
                      ],
                      "supports_credentials": True,
                      "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                      "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                      "expose_headers": ["Content-Range", "X-Total-Count"],
                      "max_age": 600
                  }},
                  supports_credentials=True,
                  automatic_options=True)

    # Security headers
    @app.after_request
    def add_security_headers(response):
        return response

    # Load logged-in user from JWT if present
    from app.models.user import User

    @app.before_request
    def load_logged_in_user():
        g.user = None
        g.current_user = None
        if request.method == 'OPTIONS':
            return

        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                user = db.session.get(User, user_id)
                if user:
                    g.user = user
                    g.current_user = user
                    current_app.logger.debug(f"Loaded user {user_id}")
        except Exception as e:
            current_app.logger.debug(f"JWT verification failed: {e}")

    # Rate limiting
    def key_func():
        if request.method == 'OPTIONS':
            return None
        return get_remote_address()

    limiter = Limiter(
        app=app,
        key_func=key_func,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
        strategy="fixed-window"
    )
    limiter.init_app(app)
    app.limiter = limiter

    # Celery setup
    from .extensions import celery
    celery.conf.update(app.config)

    log = structlog.get_logger()

    # Register blueprints
    from app.resources.application import application_bp
    from app.blueprints.api_v1 import api_v1_bp
    app.register_blueprint(application_bp, url_prefix='/api/v1/applications')
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    # ✅ Root route
    @app.route('/')
    def index():
        return {"message": "Welcome to RecruitConnect API"}, 200

    # ✅ Health check route
    @app.route('/health', methods=['GET'])
    def health():
        return {"status": "ok", "message": "RecruitConnect API running"}, 200
    

    return app
