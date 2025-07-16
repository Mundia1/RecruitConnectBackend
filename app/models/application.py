from datetime import datetime
from app import db

class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(32), default='pending', nullable=False)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)

    job_seeker = db.relationship('User', backref='applications')
    job_posting = db.relationship('Job', backref='applications')