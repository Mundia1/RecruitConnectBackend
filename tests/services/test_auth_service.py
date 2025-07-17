import pytest
from unittest.mock import patch, MagicMock
from app.services.auth_service import AuthService
from app.models.user import User
from app.extensions import db
from sqlalchemy.exc import IntegrityError

from app import create_app

class TestAuthService:
    def setup_method(self):
        self.app = create_app('testing')

    def test_register_user_success(self, init_database):
        """Test successful user registration"""
        with patch('app.tasks.email_tasks.send_email_task.delay') as mock_send_email:
            # Test data
            email = "test@example.com"
            password = "testpassword"
            first_name = "Test"
            last_name = "User"
            
            # Call the service
            user, error = AuthService.register_user(email, password, first_name, last_name)
            
            # Assertions
            assert error is None
            assert user is not None
            assert user.email == email
            assert user.first_name == first_name
            assert user.last_name == last_name
            assert user.check_password(password)
            
            # Verify email was sent
            mock_send_email.assert_called_once()
    
    def test_register_user_duplicate_email(self, init_database):
        """Test registration with duplicate email"""
        # Create a user first
        existing_user = User(
            email="existing@example.com",
            first_name="Existing",
            last_name="User"
        )
        existing_user.set_password("password123")
        db.session.add(existing_user)
        db.session.commit()
        
        # Try to register with same email
        user, error = AuthService.register_user(
            "existing@example.com",
            "newpassword",
            "New",
            "User"
        )
        
        # Assertions
        assert user is None
        assert error == "Email already exists"
    
    def test_login_user_success(self, init_database):
        """Test successful user login"""
        # Create a test user
        user = User(
            email="login@test.com",
            first_name="Login",
            last_name="Test"
        )
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        
        # Test login
        access_token, refresh_token, user_obj = AuthService.login_user("login@test.com", "testpass123")
        
        # Assertions
        assert access_token is not None
        assert refresh_token is not None
        assert user_obj is not None
        assert user_obj.email == "login@test.com"
    
    def test_login_user_invalid_credentials(self, init_database):
        """Test login with invalid credentials"""
        # Attempt login with non-existent user
        access_token, refresh_token, user_obj = AuthService.login_user("nonexistent@test.com", "wrongpass")
        
        # Assertions
        assert access_token is None
        assert refresh_token is None
        assert user_obj is None
    
    def test_refresh_access_token(self):
        """Test refreshing access token"""
        # Test refresh token
        user_id = 123
        with self.app.app_context():
            new_token = AuthService.refresh_access_token(user_id)
        
        # Assertions
        assert new_token is not None
        assert isinstance(new_token, str)