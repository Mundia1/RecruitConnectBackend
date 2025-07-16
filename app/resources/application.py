from flask import Blueprint, request, jsonify
from app.schemas.application import JobApplicationSchema
from app.services.application_service import ApplicationService

application_bp = Blueprint('application', __name__, url_prefix='/api/v1/applications')
application_schema = JobApplicationSchema()
applications_schema = JobApplicationSchema(many=True)

@application_bp.route('/', methods=['POST'])
def create_application():
    data = request.get_json()
    errors = application_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    application = ApplicationService.create_application(data)
    return jsonify(application_schema.dump(application)), 201

@application_bp.route('/<int:application_id>', methods=['GET'])
def get_application(application_id):
    application = ApplicationService.get_application_by_id(application_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    return jsonify(application_schema.dump(application))

@application_bp.route('/<int:application_id>', methods=['PATCH'])
def update_application_status(application_id):
    data = request.get_json()
    status = data.get('status')
    if not status:
        return jsonify({'error': 'Status is required'}), 400
    application = ApplicationService.update_application_status(application_id, status)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    return jsonify(application_schema.dump(application))

@application_bp.route('/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    application = ApplicationService.delete_application(application_id)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    return jsonify({'message': 'Application deleted'})

@application_bp.route('/', methods=['GET'])
def list_applications():
    job_seeker_id = request.args.get('job_seeker_id', type=int)
    job_posting_id = request.args.get('job_posting_id', type=int)
    applications = ApplicationService.list_applications(job_seeker_id, job_posting_id)
    return jsonify(applications_schema.dump(applications))