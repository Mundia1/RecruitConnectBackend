from app.extensions import db
from app.models.job_view import JobView
from datetime import date
from sqlalchemy import func, extract

class JobViewService:
    @staticmethod
    def record_view(job_id):
        today = date.today()
        job_view = JobView.query.filter_by(job_id=job_id, view_date=today).first()
        if job_view:
            job_view.view_count += 1
        else:
            job_view = JobView(job_id=job_id, view_date=today, view_count=1)
            db.session.add(job_view)
        db.session.commit()
        return job_view

    @staticmethod
    def get_monthly_views(year, month):
        monthly_views = db.session.query(
            JobView.job_id,
            func.sum(JobView.view_count).label('total_views')
        ).filter(
            extract('year', JobView.view_date) == year,
            extract('month', JobView.view_date) == month
        ).group_by(JobView.job_id).all()
        return monthly_views
