from flask import Flask
from .extensions import db, migrate
from .resources import register_resources
from config import config_by_name  # Import the dictionary

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])  # Pass the class, not a string
    db.init_app(app)
    migrate.init_app(app, db)
    register_resources(app)
    return app
