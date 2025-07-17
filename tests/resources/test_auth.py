import json

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

def test_login(client, init_database):
    # First, register a user to ensure the user exists
    client.post('/api/v1/auth/register', json={
        "email": "test_login@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    })

    # Now, log in with the registered user
    response = client.post('/api/v1/auth/login', json={
        "email": "test_login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Login successful"
    assert "access_token" in json_data['data']

def test_get_me(client, init_database):
    # Register and login to get a token
    client.post('/api/v1/auth/register', json={
        "email": "test_me@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    })
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
