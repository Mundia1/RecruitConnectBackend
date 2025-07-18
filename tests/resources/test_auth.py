import json
from app.models.user import User
from tests.factories import create_user

def test_register(client, init_database):
    response = client.post('/api/v1/auth/register', json={
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    })
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == "User registered successfully"
    assert "id" in json_data['data']
    assert json_data['data']["email"] == "test@example.com"

def test_register_duplicate_email(client, init_database):
    create_user("duplicate@example.com", "password123", "Test", "User", "job_seeker")
    response = client.post('/api/v1/auth/register', json={
        "email": "duplicate@example.com",
        "password": "password123",
        "first_name": "Another",
        "last_name": "User"
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == "Email already exists"

def test_login(client, init_database):
    # First, register a user to ensure the user exists
    create_user("test_login@example.com", "password123", "Test", "User", "job_seeker")

    # Now, log in with the registered user
    response = client.post('/api/v1/auth/login', json={
        "email": "test_login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Login successful"
    assert "access_token" in json_data['data']

def test_login_incorrect_password(client, init_database):
    create_user("test_incorrect_password@example.com", "password123", "Test", "User", "job_seeker")
    response = client.post('/api/v1/auth/login', json={
        "email": "test_incorrect_password@example.com",
        "password": "wrong_password"
    })
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == "Invalid credentials"

def test_login_nonexistent_email(client, init_database):
    response = client.post('/api/v1/auth/login', json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == "Invalid credentials"

def test_get_me(client, init_database):
    # Register and login to get a token
    create_user("test_me@example.com", "password123", "Test", "User", "job_seeker")
    response = client.post('/api/v1/auth/login', json={
        "email": "test_me@example.com",
        "password": "password123"
    })
    data = response.get_json()['data']
    token = data["access_token"]

    # Get user info
    response = client.get('/api/v1/auth/me', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "User found"
    assert json_data['data']["email"] == "test_me@example.com"

def test_refresh_access_token_invalid_token(client):
    response = client.post('/api/v1/auth/refresh', headers={
        "Authorization": "Bearer invalid_refresh_token"
    })
    assert response.status_code == 422
    json_data = response.get_json()
    assert json_data['msg'] == "Not enough segments"