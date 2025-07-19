from datetime import datetime
from app.extensions import db
from sqlalchemy_serializer import SerializerMixin

class Application(db.Model, SerializerMixin):
    __tablename__ = 'applications'

    serialize_rules = ('-user.applications', '-job_posting.applications', '-feedback.application')

    id = db.Column(db.Integer, primary_key=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(32), nullable=False, default='submitted') # Enum: submitted, viewed, rejected, accepted
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('applications', cascade='all, delete-orphan'))
    job_posting = db.relationship('JobPosting', backref=db.backref('applications', cascade='all, delete-orphan'))
