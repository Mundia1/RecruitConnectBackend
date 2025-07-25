from app.models.application import Application
from app.extensions import db
from werkzeug.exceptions import NotFound
from app.services.job_service import JobService

class ApplicationService:
    @staticmethod
    def create_application(user_id, job_posting_id):
        # Validate input parameters
        if user_id is None:
            raise ValueError("User ID cannot be None")
        if job_posting_id is None:
            raise ValueError("Job posting ID cannot be None")
            
        # Check for existing application
        existing_application = Application.query.filter_by(user_id=user_id, job_posting_id=job_posting_id).first()
        if existing_application:
            return None

        # Check if the job exists and is not expired
        try:
            job = JobService.get_job_by_id(job_posting_id)
            
            # Check if job has expired
            from datetime import datetime
            if job.deadline and job.deadline < datetime.utcnow():
                raise ValueError("Cannot apply to an expired job posting")
            
            # If we get here, the job exists and is not expired
            application = Application(user_id=user_id, job_posting_id=job_posting_id)
            db.session.add(application)
            db.session.commit()
            return application
            
        except ValueError as e:
            # Re-raise validation errors
            raise ValueError(str(e))
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
    def update_application_status(application_id, status, simulate_delay=False):
        """
        Update the status of an application.
        
        Args:
            application_id: The ID of the application to update
            status: The new status
            simulate_delay: If True, adds a small delay to help simulate race conditions in tests
            
        Returns:
            The updated application
            
        Raises:
            ValueError: If the status is invalid
            NotFound: If the application is not found
        """
        valid_statuses = ['submitted', 'under_review', 'accepted', 'rejected', 'withdrawn']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Valid statuses are: {valid_statuses}")

        try:
            # Get the application with a row-level lock
            application = (
                db.session.query(Application)
                .filter(Application.id == application_id)
                .with_for_update()
                .first()
            )
            
            if application is None:
                raise NotFound(f"Application with ID {application_id} not found")
            
            # Add a small delay to help simulate race conditions in tests
            if simulate_delay:
                import time
                time.sleep(0.5)
            
            # Update the status
            application.status = status
            
            # Always commit the transaction
            db.session.commit()
            
            return application
            
        except Exception as e:
            db.session.rollback()
            raise e

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
