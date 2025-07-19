import os
import structlog
import sentry_sdk
from flask import Flask, request
from sentry_sdk.integrations.flask import FlaskIntegration

from config import config_by_name
from app.utils.logging import configure_logging
from app.utils.error_handlers import register_error_handlers
from app.blueprints.api_v1 import api_v1_bp
from app.extensions import db, migrate, jwt, cors, talisman, cache, mail, celery
from app.metrics import metrics, rate_limit_counter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def create_app(config_name):
    configure_logging()
    
    sentry_dsn = config_by_name[config_name].SENTRY_DSN
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    # Initialize metrics before rate limiter
    metrics.init_app(app)
    
    # Initialize rate limiter with metrics
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri='memory://' if app.config.get('TESTING') else app.config.get('RATELIMIT_STORAGE_URL'),
        storage_options={"socket_connect_timeout": 30},
        default_limits=["1000 per day", "500 per hour", "100 per minute"] if app.config.get('TESTING') 
                      else ["200 per day", "50 per hour"],
        on_breach=lambda limit: rate_limit_counter.labels(
            endpoint=request.endpoint if request and hasattr(request, 'endpoint') else 'unknown'
        ).inc() if not app.config.get('TESTING') else None
    )
    limiter.init_app(app)
    app.limiter = limiter
    
    # Initialize other extensions
    cache.init_app(app)
    mail.init_app(app)

    

    

    celery.conf.update(app.config)

    log = structlog.get_logger()
    app.logger.addHandler(log)


    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    register_error_handlers(app)

    return app
