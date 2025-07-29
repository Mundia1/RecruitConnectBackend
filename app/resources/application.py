from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Application
from app.schemas.application import ApplicationSchema
from app.services.application_service import ApplicationService
from app.utils.helpers import api_response
from werkzeug.exceptions import NotFound
from app.models.user import User
from app.models.job import JobPosting
from flask_jwt_extended import jwt_required, get_jwt_identity

application_bp = Blueprint('application', __name__, url_prefix='/applications')
application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)

@application_bp.route('/', methods=['POST'])
@jwt_required()
def create_application():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    job_posting_id = data.get('job_posting_id')
    if not job_posting_id:
        return api_response(400, "Job posting ID is required")
    try:
        application = ApplicationService.create_application(current_user_id, job_posting_id)
        if application is None:
            return api_response(400, "Application already exists for this user and job")
        # --- Notification logic here ---
        from app.models.message import Notification
        job = db.session.get(JobPosting, job_posting_id)
        admin_id = job.admin_id
        notification = Notification(
            user_id=admin_id,
            message=f"New application for job '{job.title}' from user {current_user_id}"
        )
        db.session.add(notification)
        db.session.commit()
        return api_response(201, "Application created successfully", application_schema.dump(application))
    except ValueError as e:
        return api_response(400, str(e))

@application_bp.route('/<int:application_id>', methods=['GET'])
def get_application(application_id):
    application = ApplicationService.get_application_by_id(application_id)
    if not application:
        raise NotFound("Application not found")
    return api_response(200, "Application found", application_schema.dump(application))

@application_bp.route('/<int:application_id>', methods=['PATCH'])
@jwt_required()
def update_application_status(application_id):
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)
    if not current_user or current_user.role != 'admin':
        return api_response(403, "Forbidden: Only Admins can update application status")
    data = request.get_json()
    status = data.get('status')
    if not status:
        return api_response(400, "Status is required")
    try:
        application = ApplicationService.update_application_status(application_id, status)
        # --- Notification logic here ---
        from app.models.message import Notification
        notification = Notification(
            user_id=application.user_id,
            message=f"Your application status for job '{application.job_posting.title}' is now '{status}'"
        )
        db.session.add(notification)
        db.session.commit()
        return api_response(200, "Application status updated", application_schema.dump(application))
    except ValueError as e:
        return api_response(400, str(e))

@application_bp.route('/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    result = ApplicationService.delete_application(application_id)
    if not result:
        raise NotFound("Application not found")
    return api_response(204, "Application deleted")

@application_bp.route('/', methods=['GET'])
def list_applications():
    user_id = request.args.get('user_id', type=int)
    if user_id:
        applications = ApplicationService.get_applications_for_user(user_id)
    else:
        applications = ApplicationService.get_all_applications()
    result = []
    for app in applications:
        job = app.job_posting  # SQLAlchemy relationship
        result.append({
            "id": app.id,
            "title": job.title if job else "",
            "company": f"{job.admin.first_name} {job.admin.last_name}" if job and job.admin else "",
            "applied_at": app.applied_at.strftime("%Y-%m-%d %H:%M:%S") if app.applied_at else "",
            "status": app.status,
            "description": job.description if job else "",
            "requirements": job.requirements if job else "",
            "location": job.location if job else "",
            "job_posting_id": app.job_posting_id,
        })
    return jsonify(result), 200
