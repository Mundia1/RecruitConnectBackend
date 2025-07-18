from flask import Blueprint, request
from app.schemas.application import ApplicationSchema
from app.services.application_service import ApplicationService
from app.utils.helpers import api_response
from werkzeug.exceptions import NotFound
from app.models.user import User
from app.models.job import JobPosting
from app.extensions import db

application_bp = Blueprint('application', __name__, url_prefix='/applications')
application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)

@application_bp.route('/', methods=['POST'])
def create_application():
    data = request.get_json()
    errors = application_schema.validate(data)
    if errors:
        return api_response(400, "Invalid data", errors)

    user = db.session.get(User, data['user_id'])
    job_posting = db.session.get(JobPosting, data['job_posting_id'])

    if not user:
        return api_response(400, "Invalid data", {'user_id': ['User not found']})
    if not job_posting:
        return api_response(400, "Invalid data", {'job_posting_id': ['Job posting not found']})

    application = ApplicationService.create_application(data['user_id'], data['job_posting_id'])
    if application is None:
        return api_response(400, "Invalid data", {'user_id': ['Application already exists for this user and job']})
    return api_response(201, "Application created successfully", application_schema.dump(application))

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
    job_posting_id = request.args.get('job_posting_id', type=int)
    if user_id:
        applications = ApplicationService.get_applications_for_user(user_id)
    elif job_posting_id:
        applications = ApplicationService.get_applications_for_job(job_posting_id)
    else:
        applications = ApplicationService.get_all_applications()
    return api_response(200, "Applications retrieved", applications_schema.dump(applications))
