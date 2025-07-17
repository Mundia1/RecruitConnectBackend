from app.models.feedback import Feedback
from app.extensions import db

class FeedbackService:
    @staticmethod
    def create_feedback(user_id, job_application_id, rating, comment=None):
        feedback = Feedback(user_id=user_id, job_application_id=job_application_id, rating=rating, comment=comment)
        db.session.add(feedback)
        db.session.commit()
        return feedback

    @staticmethod
    def get_feedback_by_id(feedback_id):
        return db.session.get(Feedback, feedback_id)

    @staticmethod
    def get_feedback_for_application(job_application_id):
        return Feedback.query.filter_by(job_application_id=job_application_id).all()

    @staticmethod
    def update_feedback(feedback_id, rating=None, comment=None):
        feedback = db.session.get(Feedback, feedback_id)
        if feedback:
            if rating is not None:
                feedback.rating = rating
            if comment is not None:
                feedback.comment = comment
            db.session.commit()
        return feedback

    @staticmethod
    def delete_feedback(feedback_id):
        feedback = db.session.get(Feedback, feedback_id)
        if feedback:
            db.session.delete(feedback)
            db.session.commit()
            return True
        return False
