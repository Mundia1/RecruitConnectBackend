from datetime import datetime
from app.extensions import db
from sqlalchemy_serializer import SerializerMixin

class Feedback(db.Model, SerializerMixin):
    __tablename__ = 'feedback'

    serialize_rules = ('-user.feedback', '-job_application.feedback')

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='feedback')
    job_application = db.relationship('Application', backref='feedback')
