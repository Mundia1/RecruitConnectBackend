import pytest
from app.services.auth_service import AuthService

def test_auth_service_exists():
    
    assert AuthService is not None

def test_auth_service_login_stub():
   
    with pytest.raises(AttributeError):
        AuthService.login("test@example.com", "password")
