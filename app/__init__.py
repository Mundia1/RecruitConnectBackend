from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Adjust if you use a different config
    db.init_app(app)

    # Register blueprints here
    from app.resources.application import application_bp
    app.register_blueprint(application_bp)

    return app