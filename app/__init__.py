import logging
import os # Import the os module
from flask import Flask, g, request, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from .extensions import db, migrate, jwt, metrics, cache, mail
from flask_cors import CORS
from .resources import register_resources
from config import config_by_name
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
import structlog
from datetime import timedelta

cors = CORS()

def create_app(config_name):
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    register_resources(app)

    jwt.init_app(app)

    cors_origins_str = os.environ.get('CORS_ORIGINS', '')
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]

    cors.init_app(app,
        resources={
            r"/api/*": {
                "origins": CORS_ALLOWED_ORIGINS, # Back to list of strings
                "supports_credentials": True,
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
                "expose_headers": ["Content-Range", "X-Total-Count"],
                "max_age": 600
            }
        },
        supports_credentials=True,
        automatic_options=True)

    # This function will dynamically set the Access-Control-Allow-Origin header
    # for actual requests (GET, POST, etc.) when credentials are involved.
    @app.after_request
    def handle_cors_for_credentials(response):
        origin = request.headers.get('Origin')
        if origin and origin in CORS_ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true' # Ensure this is set if credentials are used
        return response

    @app.after_request
    def add_security_headers(response):
        return response

    from app.models.user import User

    @app.before_request
    def load_logged_in_user():
        g.user = None
        g.current_user = None

        if request.method == 'OPTIONS':
            return

        try:
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()

                if user_id:
                    user = db.session.get(User, user_id)
                    if user:
                        g.user = user
                        g.current_user = user
                        current_app.logger.debug(f"Loaded user {user_id} into request context")
                    else:
                        current_app.logger.warning(f"User {user_id} not found in database")
                else:
                    current_app.logger.debug("No user ID in JWT")
            except Exception as jwt_error:
                current_app.logger.debug(f"JWT verification failed: {str(jwt_error)}")

        except Exception as e:
            current_app.logger.error(f"Error in load_logged_in_user: {str(e)}", exc_info=True)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["100 per minute"],
    )
    limiter.init_app(app)
    app.limiter = limiter

    cache.init_app(app)
    mail.init_app(app)

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

    from .extensions import celery
    celery.conf.update(app.config)

    log = structlog.get_logger()

    from app.blueprints.api_v1 import api_v1_bp

    @app.route('/')
    def home():
        return "Welcome to RecruitConnect API"

    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    return app

from app.blueprints.api_v1 import api_v1_bp

def register_resources(app):
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')