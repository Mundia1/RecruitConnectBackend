import pytest
from app.models.application import Application
from app.models.user import User
from app.models.job import JobPosting

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_application(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()

        data = {
            'user_id': user.id,
            'job_posting_id': job_posting.id,
            'status': 'submitted'
        }
        response = client.post('/api/v1/applications/', json=data)
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['message'] == "Application created successfully"
        assert json_data['data']['status'] == 'submitted'

def test_get_application(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()

        app_obj = Application(user_id=user.id, job_posting_id=job_posting.id)
        init_database.session.add(app_obj)
        init_database.session.commit()
        response = client.get(f'/api/v1/applications/{app_obj.id}')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == "Application found"
        assert json_data['data']['id'] == app_obj.id

def test_update_application_status(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()

        app_obj = Application(user_id=user.id, job_posting_id=job_posting.id)
        init_database.session.add(app_obj)
        init_database.session.commit()
        response = client.patch(f'/api/v1/applications/{app_obj.id}', json={'status': 'accepted'})
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == "Application status updated"
        assert json_data['data']['status'] == 'accepted'

def test_delete_application(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()

        app_obj = Application(user_id=user.id, job_posting_id=job_posting.id)
        init_database.session.add(app_obj)
        init_database.session.commit()
        response = client.delete(f'/api/v1/applications/{app_obj.id}')
        assert response.status_code == 204

def test_list_applications(app, client, init_database):
    with app.app_context():
        user1 = init_database.session.query(User).filter_by(email="test1@example.com").first()
        user2 = init_database.session.query(User).filter_by(email="test2@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()

        app1 = Application(user_id=user1.id, job_posting_id=job_posting.id)
        app2 = Application(user_id=user2.id, job_posting_id=job_posting.id)
        init_database.session.add_all([app1, app2])
        init_database.session.commit()
        response = client.get('/api/v1/applications/')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == "Applications retrieved"
        assert len(json_data['data']) == 2