from app.resources.application import application_bp

def register_resources(app):
    app.register_blueprint(application_bp, url_prefix='/api/v1/applications')