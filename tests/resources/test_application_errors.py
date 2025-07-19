import pytest
from app.models.application import Application
from app.models.job import JobPosting
from app.models.user import User
from app.extensions import db

# Use the existing fixtures from conftest.py
def test_create_application_missing_fields(client, app):
    """Test creating an application with missing required fields"""
    with app.app_context():
        response = client.post('/api/v1/applications/', json={})
        assert response.status_code == 400
        # Check for either error message format
        assert any(msg in response.json.get('message', '') 
                 for msg in ['Missing data for required field', 'Invalid data'])

def test_create_duplicate_application(client, app, employer, job_posting):
    """Test creating a duplicate application"""
    with app.app_context():
        # Ensure objects are in the current session
        db.session.merge(employer)
        job_posting = db.session.merge(job_posting)
        
        # Create a test user
        from tests.factories import create_user
        user = create_user(
            email='testuser@example.com',
            password='testpass',
            first_name='Test',
            last_name='User',
            role='applicant'
        )
        db.session.add(user)
        db.session.commit()
        
        # First application (should succeed)
        app_data = {'user_id': user.id, 'job_posting_id': job_posting.id}
        response = client.post('/api/v1/applications/', json=app_data)
        assert response.status_code == 201
        
        # Second identical application (should fail with 400)
        response = client.post('/api/v1/applications/', json=app_data)
        assert response.status_code == 400
        # The API returns a 400 with 'Invalid data' message for duplicate applications
        assert 'invalid data' in response.json['message'].lower()

# We'll need to create an application fixture first
@pytest.fixture
def application(app, employer, job_posting):
    with app.app_context():
        # Ensure objects are in the current session
        db.session.merge(employer)
        job_posting = db.session.merge(job_posting)
        
        from tests.factories import create_user
        user = create_user(
            email='testuser2@example.com',
            password='testpass',
            first_name='Test',
            last_name='User',
            role='applicant'
        )
        db.session.add(user)
        
        application = Application(
            user_id=user.id,
            job_posting_id=job_posting.id,
            status='submitted'
        )
        db.session.add(application)
        db.session.commit()
        return application

def test_application_status_transitions(client, app, application):
    """Test valid and invalid application status transitions"""
    with app.app_context():
        # Refresh application in the current session
        from app.models.application import Application as AppModel
        application = db.session.merge(application)
        app_id = application.id
        
        # Test valid status: submitted -> under_review
        response = client.patch(f'/api/v1/applications/{app_id}', 
                              json={'status': 'under_review'})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.data}"
        
        # Test valid status: under_review -> submitted
        # Note: The API currently allows any valid status transition
        response = client.patch(f'/api/v1/applications/{app_id}',
                              json={'status': 'submitted'})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.data}"
        
        # Test valid status: submitted -> accepted
        response = client.patch(f'/api/v1/applications/{app_id}',
                              json={'status': 'accepted'})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.data}"
        
        # Test invalid status value
        response = client.patch(f'/api/v1/applications/{app_id}',
                              json={'status': 'invalid_status'})
        assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.data}"
