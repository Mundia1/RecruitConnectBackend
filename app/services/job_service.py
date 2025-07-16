from app import db
from app.models.job import JobPosting


def create_job(data):
    job = JobPosting(**data)
    db.session.add(job)
    db.session.commit()
    return job


def get_all_jobs():
    return JobPosting.query.all()


def get_job_by_id(job_id):
    return JobPosting.query.get_or_404(job_id)


def update_job(job_id, data):
    job = JobPosting.query.get_or_404(job_id)
    for key, value in data.items():
        setattr(job, key, value)
    db.session.commit()
    return job


def delete_job(job_id):
    job = JobPosting.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
