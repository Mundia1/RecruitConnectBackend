import json

def test_register_and_login(client):
    
    response = client.post('/auth/register', json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["email"] == "test@example.com"

    
    response = client.post('/auth/login', json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data

    
    token = data["access_token"]
    response = client.get('/auth/me', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    user_data = response.get_json()
    assert user_data["email"] == "test@example.com"