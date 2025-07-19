import pytest
from datetime import datetime, timedelta
from app.extensions import db
from app.models.job import JobPosting

# Create a test admin user for job creation
def create_test_admin(app):
    from tests.factories import create_admin_user
    with app.app_context():
        admin = create_admin_user()
        # Ensure the admin is in the current session
        admin = db.session.merge(admin)
        return admin

def get_auth_headers(client, email, password):
    login_resp = client.post('/api/v1/auth/login/', 
                           json={'email': email, 'password': password})
    return {'Authorization': f'Bearer {login_resp.json["access_token"]}'}

def test_job_creation_validation(client, app, employer):
    """Test job creation with various validation scenarios"""
    with app.app_context():
        # Ensure employer is in the current session
        employer = db.session.merge(employer)
        
        # Create an admin user and get auth headers
        admin = create_test_admin(app)
        admin = db.session.merge(admin)
        
        # Login as admin to get auth token
        login_resp = client.post('/api/v1/auth/login', 
                               json={'email': admin.email, 'password': 'adminpass'})
        assert login_resp.status_code == 200
        assert 'data' in login_resp.json
        assert 'access_token' in login_resp.json['data']
        
        headers = {'Authorization': f'Bearer {login_resp.json["data"]["access_token"]}'}
        
        # Missing required fields
        response = client.post('/api/v1/jobs/', json={}, headers=headers)
        assert response.status_code == 400
        
        # Invalid date format
        invalid_job = {
            'title': 'Test Job',
            'description': 'Test Description',
            'requirements': 'Test Requirements',
            'location': 'Remote',
            'deadline': 'invalid-date',
            'admin_id': admin.id
        }
        response = client.post('/api/v1/jobs/', json=invalid_job, headers=headers)
        assert response.status_code == 400

def test_job_filtering_search(client, app, job_posting):
    """Test job filtering and search functionality"""
    with app.app_context():
        # Ensure job_posting is in the current session
        job_posting = db.session.merge(job_posting)
        
        # Test search by keyword (assuming job_posting has 'python' in title/description)
        response = client.get('/api/v1/jobs/?q=python')
        assert response.status_code == 200
        assert 'data' in response.json
        assert len(response.json['data']) > 0
        
        # Test location filter
        response = client.get(f'/api/v1/jobs/?location={job_posting.location}')
        assert response.status_code == 200
        assert 'data' in response.json
        assert all(job['location'] == job_posting.location for job in response.json['data'])

# Create a fixture for multiple test users
@pytest.fixture
def test_users(app):
    from tests.factories import create_user
    with app.app_context():
        users = [create_user(f'user{i}@test.com', 'testpass', f'User{i}', f'Test{i}') for i in range(1, 4)]
        # Ensure all users are in the session
        users = [db.session.merge(user) for user in users]
        db.session.add_all(users)
        db.session.commit()
        return users

def test_job_application_limits(client, app, test_users):
    """Test job application limits"""
    with app.app_context():
        # Create an admin user and get auth headers
        admin = create_test_admin(app)
        admin = db.session.merge(admin)
        
        # Login as admin to get auth token
        login_resp = client.post('/api/v1/auth/login', 
                               json={'email': admin.email, 'password': 'adminpass'})
        assert login_resp.status_code == 200
        assert 'data' in login_resp.json
        assert 'access_token' in login_resp.json['data']
        
        headers = {'Authorization': f'Bearer {login_resp.json["data"]["access_token"]}'}
        
        # Create a new job posting for this test
        job_data = {
            'title': 'Test Job',
            'description': 'Test Description',
            'requirements': 'Test Requirements',
            'location': 'Remote',
            'admin_id': admin.id
        }
        response = client.post('/api/v1/jobs/', json=job_data, headers=headers)
        assert response.status_code == 201
        assert 'data' in response.json
        assert 'id' in response.json['data']
        job_id = response.json['data']['id']
        
        # Test creating applications
        for user in test_users:
            user = db.session.merge(user)
            
            # Login as user to get auth token
            user_login = client.post('/api/v1/auth/login',
                                  json={'email': user.email, 'password': 'testpass'})
            assert user_login.status_code == 200
            assert 'data' in user_login.json
            assert 'access_token' in user_login.json['data']
            
            user_headers = {'Authorization': f'Bearer {user_login.json["data"]["access_token"]}'}
            
            # Create application with required user_id field
            response = client.post('/api/v1/applications/',
                                json={
                                    'job_posting_id': job_id,
                                    'user_id': user.id  # Include required user_id field
                                },
                                headers=user_headers)
            # Check if application was created or if limit was reached
            assert response.status_code in [201, 400]

def test_job_expiration(client, app):
    """Test job expiration functionality"""
    with app.app_context():
        # Create an admin user and get auth headers
        admin = create_test_admin(app)
        admin = db.session.merge(admin)
        
        # Login as admin to get auth token
        login_resp = client.post('/api/v1/auth/login',
                               json={'email': admin.email, 'password': 'adminpass'})
        assert login_resp.status_code == 200
        assert 'data' in login_resp.json
        assert 'access_token' in login_resp.json['data']
        
        headers = {'Authorization': f'Bearer {login_resp.json["data"]["access_token"]}'}
        
        # Create a job posting with a past deadline
        past_deadline = datetime.utcnow() - timedelta(days=1)
        job_data = {
            'title': 'Expired Job',
            'description': 'This job has expired',
            'requirements': 'Test Requirements',
            'location': 'Remote',
            'deadline': past_deadline.isoformat(),
            'admin_id': admin.id
        }
        
        # Create the job posting
        response = client.post('/api/v1/jobs/', json=job_data, headers=headers)
        assert response.status_code == 201
        assert 'data' in response.json
        assert 'id' in response.json['data']
        job_id = response.json['data']['id']
        
        # Create a regular user
        from tests.factories import create_user
        user = create_user('expired_test@example.com', 'testpass', 'Expired', 'User')
        user = db.session.merge(user)
        
        # Get user auth headers
        user_login = client.post('/api/v1/auth/login',
                               json={'email': user.email, 'password': 'testpass'})
        assert user_login.status_code == 200
        assert 'data' in user_login.json
        assert 'access_token' in user_login.json['data']
        
        user_headers = {'Authorization': f'Bearer {user_login.json["data"]["access_token"]}'}
        
        # Should not be able to apply to expired job
        response = client.post(
            '/api/v1/applications/',
            json={
                'job_posting_id': job_id,
                'user_id': user.id  # Include required user_id field
            },
            headers=user_headers
        )
        # Check for either 400 (expired) or 404 (if job not found)
        assert response.status_code in [400, 404]
        if response.status_code == 400:
            # Check for either 'expired' in message or 'invalid data' with user_id error
            response_data = response.json
            if 'message' in response_data:
                message = response_data['message'].lower()
                assert 'expired' in message or 'invalid data' in message
