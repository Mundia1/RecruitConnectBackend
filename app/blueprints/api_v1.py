from flask import Blueprint
from app.resources.job import job_bp
from app.resources.auth import auth_bp
from app.resources.application import application_bp
from app.resources.message import message_bp
from app.resources.feedback import feedback_bp
from app.resources.faq import faq_bp

api_v1_bp = Blueprint("api_v1", __name__)

api_v1_bp.register_blueprint(job_bp)
api_v1_bp.register_blueprint(auth_bp)
api_v1_bp.register_blueprint(application_bp)
api_v1_bp.register_blueprint(message_bp)
api_v1_bp.register_blueprint(feedback_bp)
api_v1_bp.register_blueprint(faq_bp)