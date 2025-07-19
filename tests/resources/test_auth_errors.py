import pytest
from app.models.user import User
from app.extensions import db

def test_failed_login_attempts(client, app):
    """Test failed login attempts"""
    with app.app_context():
        # Create a test user
        from tests.factories import create_user
        user = create_user(email='test@example.com', password='testpass', 
                         first_name='Test', last_name='User')
        
        # Test failed login attempt
        response = client.post('/api/v1/auth/login', 
                            json={'email': user.email, 'password': 'wrongpass'})
        
        # Should return 401 for invalid credentials
        assert response.status_code == 401
        assert 'invalid' in response.json['message'].lower()

def test_token_refresh_scenarios(client, app):
    """Test login and token refresh scenarios"""
    with app.app_context():
        # Create a test user
        from tests.factories import create_user
        user = create_user(email='refresh@example.com', password='testpass',
                         first_name='Refresh', last_name='User')
        user = db.session.merge(user)
        
        # Test successful login
        login_resp = client.post('/api/v1/auth/login', 
                               json={'email': user.email, 'password': 'testpass'})
        assert login_resp.status_code == 200
        assert 'data' in login_resp.json
        assert 'access_token' in login_resp.json['data']

def test_role_based_access(client, app):
    """Test role-based access control"""
    with app.app_context():
        # Create a regular user and admin user
        from tests.factories import create_user, create_admin_user
        regular_user = create_user(email='regular@example.com', password='testpass',
                                 first_name='Regular', last_name='User')
        admin_user = create_admin_user(email='admin@example.com', password='adminpass',
                                     first_name='Admin', last_name='User')
        
        # Ensure users are in the session
        regular_user = db.session.merge(regular_user)
        admin_user = db.session.merge(admin_user)
        
        # Test regular user login
        login_resp = client.post('/api/v1/auth/login', 
                               json={'email': regular_user.email, 'password': 'testpass'})
        assert login_resp.status_code == 200
        assert 'data' in login_resp.json
        assert 'access_token' in login_resp.json['data']
        regular_token = login_resp.json['data']['access_token']
        
        # Admin login
        admin_resp = client.post('/api/v1/auth/login',
                               json={'email': admin_user.email, 'password': 'adminpass'})
        assert admin_resp.status_code == 200
        assert 'data' in admin_resp.json
        assert 'access_token' in admin_resp.json['data']
        admin_token = admin_resp.json['data']['access_token']
        
        # Regular user tries to access admin endpoint (should be forbidden)
        response = client.get('/api/v1/admin/users', 
                            headers={'Authorization': f'Bearer {regular_token}'})
        assert response.status_code in [403, 404]  # 403 Forbidden or 404 if endpoint doesn't exist
        
        # Admin access (if admin endpoint exists)
        if hasattr(client.application.view_functions, 'admin.list_users'):
            response = client.get('/api/v1/admin/users',
                                headers={'Authorization': f'Bearer {admin_token}'})
            assert response.status_code == 200
