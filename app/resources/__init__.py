from app.resources.application import application_bp
from app.blueprints.api_v1 import api_v1_bp

def register_resources(app):
    app.register_blueprint(application_bp, url_prefix='/api/v1/applications')
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')