from app.models.application import Application
from app.extensions import db
from werkzeug.exceptions import NotFound

class ApplicationService:
    @staticmethod
    def create_application(user_id, job_posting_id):
        # First check if the job exists
        from app.services.job_service import JobService
        try:
            job = JobService.get_job_by_id(job_posting_id)
            # If we get here, the job exists
            application = Application(user_id=user_id, job_posting_id=job_posting_id)
            db.session.add(application)
            db.session.commit()
            return application
        except NotFound as e:
            # Re-raise with a more specific message
            raise NotFound(f"Cannot create application: {str(e)}")

    @staticmethod
    def get_application_by_id(application_id):
        application = db.session.get(Application, application_id)
        if application is None:
            raise NotFound(f"Application with ID {application_id} not found")
        return application

    @staticmethod
    def update_application_status(application_id, status):
        application = db.session.get(Application, application_id)
        if application is None:
            raise NotFound(f"Application with ID {application_id} not found")
        application.status = status
        db.session.commit()
        return application

    @staticmethod
    def delete_application(application_id):
        application = db.session.get(Application, application_id)
        if application is None:
            raise NotFound(f"Application with ID {application_id} not found")
        db.session.delete(application)
        db.session.commit()
        return application

    @staticmethod
    def get_all_applications():
        return db.session.query(Application).all()

    @staticmethod
    def get_applications_for_user(user_id):
        return db.session.query(Application).filter_by(user_id=user_id).all()

    @staticmethod
    def get_applications_for_job(job_posting_id):
        return db.session.query(Application).filter_by(job_posting_id=job_posting_id).all()
