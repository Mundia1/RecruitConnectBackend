from app.models.application import JobApplication
from app import db

class ApplicationService:
    @staticmethod
    def create_application(data):
        application = JobApplication(**data)
        db.session.add(application)
        db.session.commit()
        return application

    @staticmethod
    def get_application_by_id(application_id):
        return JobApplication.query.get(application_id)

    @staticmethod
    def update_application_status(application_id, status):
        application = JobApplication.query.get(application_id)
        if application:
            application.status = status
            db.session.commit()
        return application

    @staticmethod
    def delete_application(application_id):
        application = JobApplication.query.get(application_id)
        if application:
            db.session.delete(application)
            db.session.commit()
        return application

    @staticmethod
    def list_applications(job_seeker_id=None, job_posting_id=None):
        query = JobApplication.query
        if job_seeker_id:
            query = query.filter_by(job_seeker_id=job_seeker_id)
        if job_posting_id:
            query = query.filter_by(job_posting_id=job_posting_id)
        return query.all()