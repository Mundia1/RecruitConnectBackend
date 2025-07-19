from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_talisman import Talisman
from flask_caching import Cache
from celery import Celery
from flask_mail import Mail
from prometheus_flask_exporter import PrometheusMetrics
import os
from config import config_by_name
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
talisman = Talisman()
cache = Cache()
mail = Mail()
metrics = PrometheusMetrics.for_app_factory()
celery = Celery(__name__)
bcrypt = Bcrypt()