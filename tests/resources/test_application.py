import pytest
from app.models.application import Application
from app.models.user import User
from app.models.job import JobPosting
from tests.factories import create_user, create_job_posting, create_application

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

def test_create_application_missing_user_id(app, client, init_database):
    with app.app_context():
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
        data = {
            'job_posting_id': job_posting.id,
            'status': 'submitted'
        }
        response = client.post('/api/v1/applications/', json=data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert "user_id" in json_data['data']

def test_create_application_missing_job_posting_id(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        data = {
            'user_id': user.id,
            'status': 'submitted'
        }
        response = client.post('/api/v1/applications/', json=data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert "job_posting_id" in json_data['data']

def test_create_application_invalid_user_id(app, client, init_database):
    with app.app_context():
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
        data = {
            'user_id': 9999,  # Non-existent user ID
            'job_posting_id': job_posting.id,
            'status': 'submitted'
        }
        response = client.post('/api/v1/applications/', json=data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['message'] == "Invalid data"

def test_create_application_invalid_job_posting_id(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        data = {
            'user_id': user.id,
            'job_posting_id': 9999,  # Non-existent job posting ID
            'status': 'submitted'
        }
        response = client.post('/api/v1/applications/', json=data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['message'] == "Invalid data"

def test_create_duplicate_application(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
        
        # Create the first application
        create_application(user.id, job_posting.id)

        # Attempt to create a duplicate application
        data = {
            'user_id': user.id,
            'job_posting_id': job_posting.id,
            'status': 'submitted'
        }
        response = client.post('/api/v1/applications/', json=data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['message'] == "Invalid data"

def test_get_application(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()

        app_obj = create_application(user.id, job_posting.id)
        response = client.get(f'/api/v1/applications/{app_obj.id}')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == "Application found"
        assert json_data['data']['id'] == app_obj.id

def test_get_nonexistent_application(app, client):
    response = client.get('/api/v1/applications/9999')
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['message'] == "Not found"

def test_update_application_status(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()

        app_obj = create_application(user.id, job_posting.id)
        response = client.patch(f'/api/v1/applications/{app_obj.id}', json={'status': 'accepted'})
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == "Application status updated"
        assert json_data['data']['status'] == 'accepted'

def test_update_application_status_missing_status(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
        app_obj = create_application(user.id, job_posting.id)
        response = client.patch(f'/api/v1/applications/{app_obj.id}', json={})
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['message'] == "Status is required"

def test_update_application_status_invalid_status(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
        app_obj = create_application(user.id, job_posting.id)
        response = client.patch(f'/api/v1/applications/{app_obj.id}', json={'status': 'invalid_status'})
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['message'] == "Invalid status: invalid_status. Valid statuses are: ['submitted', 'under_review', 'accepted', 'rejected', 'withdrawn']"

def test_update_nonexistent_application(app, client):
    response = client.patch('/api/v1/applications/9999', json={'status': 'accepted'})
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['message'] == "Not found"

def test_delete_application(app, client, init_database):
    with app.app_context():
        user = init_database.session.query(User).filter_by(email="test1@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()

        app_obj = create_application(user.id, job_posting.id)
        response = client.delete(f'/api/v1/applications/{app_obj.id}')
        assert response.status_code == 204

def test_delete_nonexistent_application(app, client):
    response = client.delete('/api/v1/applications/9999')
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['message'] == "Not found"

def test_list_applications(app, client, init_database):
    with app.app_context():
        user1 = init_database.session.query(User).filter_by(email="test1@example.com").first()
        user2 = init_database.session.query(User).filter_by(email="test2@example.com").first()
        job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()

        app1 = create_application(user1.id, job_posting.id)
        app2 = create_application(user2.id, job_posting.id)
        
        response = client.get('/api/v1/applications/')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == "Applications retrieved"
        assert len(json_data['data']) == 2

        response = client.get(f'/api/v1/applications/?user_id={user1.id}')
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data['data']) == 1
        assert json_data['data'][0]['user_id'] == user1.id

        response = client.get(f'/api/v1/applications/?job_posting_id={job_posting.id}')
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data['data']) == 2
        assert json_data['data'][0]['job_posting_id'] == job_posting.id
        assert json_data['data'][1]['job_posting_id'] == job_posting.id
