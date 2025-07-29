from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models import Application
from app.schemas.application import ApplicationSchema
from app.services.application_service import ApplicationService
from app.utils.helpers import api_response
from werkzeug.exceptions import NotFound
from app.models.user import User
from app.models.job import JobPosting
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os

application_bp = Blueprint('application', __name__, url_prefix='/applications')
application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)

@application_bp.route('/', methods=['POST'])
@jwt_required()
def apply_for_job():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400

    resume_file = request.files['resume']
    if resume_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    user_id = request.form.get('user_id')
    job_posting_id = request.form.get('job_posting_id')

    if not user_id or not job_posting_id:
        return jsonify({"error": "Missing user_id or job_posting_id"}), 400

    # Ensure the user making the request matches the JWT identity
    current_user_id = get_jwt_identity()
    if int(user_id) != int(current_user_id):
        return jsonify({"error": "You can only apply as yourself."}), 403

    # Check user role
    user = User.query.get(user_id)
    if not user or user.role.lower() != "job_seeker":
        return jsonify({"error": "Only job seekers can apply for jobs."}), 403

    filename = secure_filename(resume_file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    resume_path = os.path.join(upload_folder, filename)
    resume_file.save(resume_path)

    application = ApplicationService.create_application(user_id=user_id, job_posting_id=job_posting_id, resume_path=resume_path)
    
    if application:
        return jsonify({"message": "Application created"}), 201
    else:
        # This case now correctly handles duplicate applications or other creation failures from the service
        return jsonify({"error": "Application already exists or failed to create"}), 400

@application_bp.route('/<int:application_id>', methods=['GET'])
def get_application(application_id):
    application = ApplicationService.get_application_by_id(application_id)
    if not application:
        raise NotFound("Application not found")
    return api_response(200, "Application found", application_schema.dump(application))

@application_bp.route('/<int:application_id>', methods=['PATCH'])
def update_application_status(application_id):
    data = request.get_json()
    status = data.get('status')
    if not status:
        return api_response(400, "Status is required")
    try:
        application = ApplicationService.update_application_status(application_id, status)
    except ValueError as e:
        return api_response(400, str(e))
    if not application:
        raise NotFound("Application not found")
    return api_response(200, "Application status updated", application_schema.dump(application))

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
