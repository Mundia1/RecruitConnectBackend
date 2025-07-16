import pytest
from app import create_app, db
from app.models.application import JobApplication
from app.models.user import User
from app.models.job import Job

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_create_application(client):
    data = {
        'job_seeker_id': 1,
        'job_posting_id': 1,
        'status': 'pending'
    }
    response = client.post('/api/v1/applications/', json=data)
    assert response.status_code == 201
    assert response.get_json()['status'] == 'pending'

def test_get_application(client):
    # Create application first
    app_obj = JobApplication(job_seeker_id=1, job_posting_id=1)
    db.session.add(app_obj)
    db.session.commit()
    response = client.get(f'/api/v1/applications/{app_obj.id}')
    assert response.status_code == 200
    assert response.get_json()['id'] == app_obj.id

def test_update_application_status(client):
    app_obj = JobApplication(job_seeker_id=1, job_posting_id=1)
    db.session.add(app_obj)
    db.session.commit()
    response = client.patch(f'/api/v1/applications/{app_obj.id}', json={'status': 'accepted'})
    assert response.status_code == 200
    assert response.get_json()['status'] == 'accepted'

def test_delete_application(client):
    app_obj = JobApplication(job_seeker_id=1, job_posting_id=1)
    db.session.add(app_obj)
    db.session.commit()
    response = client.delete(f'/api/v1/applications/{app_obj.id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Application deleted'

def test_list_applications(client):
    app1 = JobApplication(job_seeker_id=1, job_posting_id=1)
    app2 = JobApplication(job_seeker_id=2, job_posting_id=1)
    db.session.add_all([app1, app2])
    db.session.commit()
    response = client.get('/api/v1/applications/')
    assert response.status_code == 200
    assert len(response.get_json()) == 2