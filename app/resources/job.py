from flask import Blueprint, request
from app.schemas.job import JobSchema
from app.services.job_service import JobService
from app.extensions import db, cache
from app.metrics import metrics
from app.utils.helpers import api_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.services.job_view_service import JobViewService

job_bp = Blueprint('job', __name__, url_prefix='/jobs')
job_schema = JobSchema()
jobs_schema = JobSchema(many=True)

@job_bp.route('/', methods=['POST'])
@jwt_required()
def create_job_posting():
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    if not current_user or current_user.role not in ['admin', 'employer']:
        return api_response(403, "Forbidden: Only Admins or Employers can create job postings")

    print("create_job_posting function entered") # Debug print
    data = request.get_json()
    print(f"Received data in resource: {data}") # Debug print
    
    # Log the raw data and its type
    print(f"Raw data type: {type(data)}")
    for key, value in data.items():
        print(f"Key: {key}, Type: {type(value).__name__}, Value: {value}")
    
    # Validate the data
    errors = job_schema.validate(data)
    if errors:
        print(f"Validation errors: {errors}") # Debug print
        return api_response(400, "Invalid data", errors)
    
    try:
        job = JobService.create_job(data)
        cache.clear() # Invalidate cache for all jobs
        return api_response(201, "Job created successfully", job_schema.dump(job))
    except Exception as e:
        print(f"Error creating job: {str(e)}")
        return api_response(500, "Error creating job", str(e))

@job_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_jobs():
    jobs = JobService.get_all_jobs()
    return api_response(200, "Jobs retrieved", jobs_schema.dump(jobs))

@job_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = JobService.get_job_by_id(job_id)
    if not job:
        return api_response(404, "Job not found")
    JobViewService.record_view(job_id)
    return api_response(200, "Job found", job_schema.dump(job))

@job_bp.route('/<int:job_id>', methods=['PATCH'])
def update_job(job_id):
    data = request.get_json()
    errors = job_schema.validate(data, partial=True)
    if errors:
        return api_response(400, "Invalid data", errors)
    job = JobService.update_job(job_id, data)
    if not job:
        return api_response(404, "Job not found")
    cache.clear() # Invalidate cache for all jobs
    return api_response(200, "Job updated successfully", job_schema.dump(job))

@job_bp.route('/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    result = JobService.delete_job(job_id)
    if not result:
        return api_response(404, "Job not found")
    return api_response(204, "Job deleted")