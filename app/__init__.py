import os
import structlog
import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

from config import config_by_name
from app.utils.logging import configure_logging
from app.utils.error_handlers import register_error_handlers
from app.blueprints.api_v1 import api_v1_bp
from app.extensions import db, migrate, jwt, cors, talisman, limiter, cache, mail, metrics, celery

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
    
    limiter.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    metrics.init_app(app)

    celery.conf.update(app.config)

    log = structlog.get_logger()
    app.logger.addHandler(log)


    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    register_error_handlers(app)

    return app
