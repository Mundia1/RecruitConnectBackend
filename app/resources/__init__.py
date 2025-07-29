from app.blueprints.api_v1 import api_v1_bp
from app.resources.auth import auth_bp

def register_resources(app):
    app.register_blueprint(api_v1_bp)
    app.register_blueprint(auth_bp)