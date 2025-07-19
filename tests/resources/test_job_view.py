import json
from datetime import date
from app.models.job_view import JobView
from app.models.job import JobPosting
from app.models.user import User
from app.extensions import db
from tests.factories import create_user, create_job_posting

def test_get_monthly_job_views_admin_required(client, init_database):
    response = client.get('/api/v1/job_views/monthly?year=2023&month=1')
    assert response.status_code == 403

def test_get_monthly_job_views_missing_params(client, init_database):
    admin_user = create_user("admin@example.com", "password123", "Admin", "User", "admin")
    login_response = client.post('/api/v1/auth/login', json={
        "email": admin_user.email,
        "password": "password123"
    })
    admin_token = login_response.get_json()['data']['access_token']

    response = client.get('/api/v1/job_views/monthly', headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 400
    assert response.json['message'] == "Year and month are required parameters."

def test_get_monthly_job_views_as_admin(client, init_database):
    with client.application.app_context():
        db.session.query(JobView).delete()
        db.session.query(JobPosting).delete()
        db.session.query(User).delete()
        db.session.commit()

        admin_user = create_user("admin@example.com", "password123", "Admin", "User", "admin")
        job1 = create_job_posting("Job 1", "Desc", "Loc", "Req", admin_user.id)
        job2 = create_job_posting("Job 2", "Desc", "Loc", "Req", admin_user.id)

        # Record some views for the current month
        today = date.today()
        db.session.add(JobView(job_id=job1.id, view_date=today, view_count=5))
        db.session.add(JobView(job_id=job2.id, view_date=today, view_count=3))
        db.session.commit()

        login_response = client.post('/api/v1/auth/login', json={
            "email": admin_user.email,
            "password": "password123"
        })
        admin_token = login_response.get_json()['data']['access_token']

        response = client.get(f'/api/v1/job_views/monthly?year={today.year}&month={today.month}', headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200
        json_data = response.get_json()['data']
        assert len(json_data) == 2
        
        views_dict = {item['job_id']: item['total_views'] for item in json_data}
        assert views_dict[job1.id] == 5
        assert views_dict[job2.id] == 3
