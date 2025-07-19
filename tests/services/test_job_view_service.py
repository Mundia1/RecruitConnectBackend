from datetime import date, timedelta
from app.services.job_view_service import JobViewService
from app.models.job_view import JobView
from app.models.job import JobPosting
from app.models.user import User
from app.extensions import db
from tests.factories import create_user, create_job_posting

def test_record_view_new_entry(app, init_database):
    with app.app_context():
        # Clear existing data to ensure a clean slate
        db.session.query(JobView).delete()
        db.session.query(JobPosting).delete()
        db.session.query(User).delete()
        db.session.commit()

        admin_user = create_user("admin@example.com", "password123", "Admin", "User", "admin")
        job = create_job_posting("Test Job", "Desc", "Loc", "Req", admin_user.id)

        job_view = JobViewService.record_view(job.id)
        assert job_view.job_id == job.id
        assert job_view.view_date == date.today()
        assert job_view.view_count == 1

def test_record_view_existing_entry(app, init_database):
    with app.app_context():
        # Clear existing data to ensure a clean slate
        db.session.query(JobView).delete()
        db.session.query(JobPosting).delete()
        db.session.query(User).delete()
        db.session.commit()

        admin_user = create_user("admin@example.com", "password123", "Admin", "User", "admin")
        job = create_job_posting("Test Job", "Desc", "Loc", "Req", admin_user.id)

        # Create an initial view entry
        initial_view = JobView(job_id=job.id, view_date=date.today(), view_count=5)
        db.session.add(initial_view)
        db.session.commit()

        job_view = JobViewService.record_view(job.id)
        assert job_view.job_id == job.id
        assert job_view.view_date == date.today()
        assert job_view.view_count == 6

def test_get_monthly_views(app, init_database):
    with app.app_context():
        # Clear existing data to ensure a clean slate
        db.session.query(JobView).delete()
        db.session.query(JobPosting).delete()
        db.session.query(User).delete()
        db.session.commit()

        admin_user = create_user("admin@example.com", "password123", "Admin", "User", "admin")
        job1 = create_job_posting("Job 1", "Desc", "Loc", "Req", admin_user.id)
        job2 = create_job_posting("Job 2", "Desc", "Loc", "Req", admin_user.id)

        # Views for current month
        today = date.today()
        JobViewService.record_view(job1.id) # 1 view
        JobViewService.record_view(job1.id) # 2 views
        JobViewService.record_view(job2.id) # 1 view

        # Views for previous month (should not be included)
        last_month = today.replace(day=1) - timedelta(days=1)
        db.session.add(JobView(job_id=job1.id, view_date=last_month, view_count=10))
        db.session.commit()

        year = today.year
        month = today.month
        monthly_views = JobViewService.get_monthly_views(year, month)

        assert len(monthly_views) == 2
        views_dict = {view.job_id: view.total_views for view in monthly_views}
        assert views_dict[job1.id] == 2
        assert views_dict[job2.id] == 1

def test_job_view_repr(app, init_database):
    with app.app_context():
        # Clear existing data to ensure a clean slate
        db.session.query(JobView).delete()
        db.session.query(JobPosting).delete()
        db.session.query(User).delete()
        db.session.commit()

        admin_user = create_user("admin@example.com", "password123", "Admin", "User", "admin")
        job = create_job_posting("Test Job", "Desc", "Loc", "Req", admin_user.id)

        job_view = JobView(job_id=job.id, view_date=date(2023, 1, 15), view_count=100)
        db.session.add(job_view)
        db.session.commit()

        assert repr(job_view) == f"<JobView {job.id} on 2023-01-15: 100 views>"