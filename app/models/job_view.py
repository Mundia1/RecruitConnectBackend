from app.extensions import db
from datetime import date
from sqlalchemy_serializer import SerializerMixin

class JobView(db.Model, SerializerMixin):
    __tablename__ = 'job_views'

    serialize_rules = ('-job.views',)

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    view_date = db.Column(db.Date, nullable=False, default=date.today)
    view_count = db.Column(db.Integer, default=0)

    job = db.relationship('JobPosting', backref=db.backref('views', lazy=True))

    __table_args__ = (db.UniqueConstraint('job_id', 'view_date', name='_job_view_uc'),)

    def __repr__(self):
        return f"<JobView {self.job_id} on {self.view_date}: {self.view_count} views>"
