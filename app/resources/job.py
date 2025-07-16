from flask import Blueprint, request, jsonify
from app.schemas.job import JobPostingSchema
from app.services import job_service


job_bp = Blueprint('job_bp', __name__)
job_schema = JobPostingSchema()
jobs_schema = JobPostingSchema(many=True)


@job_bp.route('/jobs', methods=['POST'])
def create_job_posting():
    data = request.get_json()
    validated_data = job_schema.load(data)
    job = job_service.create_job(validated_data)
    return job_schema.dump(job), 201


@job_bp.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = job_service.get_all_jobs()
    return jsonify(jobs_schema.dump(jobs))


@job_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = job_service.get_job_by_id(job_id)
    return job_schema.dump(job)


@job_bp.route('/jobs/<int:job_id>', methods=['PATCH'])
def update_job(job_id):
    data = request.get_json()
    validated_data = job_schema.load(data, partial=True)
    job = job_service.update_job(job_id, validated_data)
    return job_schema.dump(job)


@job_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job_service.delete_job(job_id)
    return '', 204
