from app.extensions import db
from app.models.job import JobPosting

class JobService:
    @staticmethod
    def create_job(data):
        if 'deadline' in data and isinstance(data['deadline'], str):
            from datetime import datetime
            data['deadline'] = datetime.fromisoformat(data['deadline'])
        print(f"Data before JobPosting instantiation: {data}") # Debug print
        job = JobPosting(**data)
        db.session.add(job)
        db.session.commit()
        return job

    @staticmethod
    def get_all_jobs():
        return JobPosting.query.all()

    @staticmethod
    def get_job_by_id(job_id):
        job = db.session.get(JobPosting, job_id)
        if job is None:
            from werkzeug.exceptions import NotFound
            raise NotFound(f"Job with ID {job_id} not found")
        return job

    @staticmethod
    def update_job(job_id, data):
        job = db.session.get(JobPosting, job_id)
        if job is None:
            from werkzeug.exceptions import NotFound
            raise NotFound(f"Job with ID {job_id} not found")
        for key, value in data.items():
            setattr(job, key, value)
        db.session.commit()
        return job

    @staticmethod
    def delete_job(job_id):
        job = db.session.get(JobPosting, job_id)
        if job is None:
            from werkzeug.exceptions import NotFound
            raise NotFound(f"Job with ID {job_id} not found")
        db.session.delete(job)
        db.session.commit()
        return True