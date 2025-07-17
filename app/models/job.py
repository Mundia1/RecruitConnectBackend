from datetime import datetime
from app.extensions import db
from sqlalchemy_serializer import SerializerMixin

class JobPosting(db.Model, SerializerMixin):
    __tablename__ = 'job_postings'

    serialize_rules = ('-admin.job_postings', '-applications.job_posting')

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255))
    requirements = db.Column(db.Text)
    deadline = db.Column(db.DateTime)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    admin = db.relationship('User', backref='job_postings')
