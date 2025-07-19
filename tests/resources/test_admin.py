import json
from app.models.user import User
from app.models.job import JobPosting
from tests.factories import create_user, create_admin_user
from app.extensions import db

def test_get_all_users_admin_required(client, init_database):
    response = client.get('/api/v1/admin/users')
    assert response.status_code == 403

def test_get_all_users_as_admin(client, init_database):
    # Clear existing users from init_database to ensure a clean slate for this test
    with client.application.app_context():
        db.session.query(JobPosting).delete()
        db.session.query(User).delete()
        db.session.commit()

    admin_user = create_admin_user("admin@example.com", "password123")
    user1 = create_user("user1@example.com", "password123", "User", "One", "job_seeker")
    user2 = create_user("user2@example.com", "password123", "User", "Two", "employer")

    login_response = client.post('/api/v1/auth/login', json={
        "email": admin_user.email,
        "password": "password123"
    })
    admin_token = login_response.get_json()['data']['access_token']

    response = client.get('/api/v1/admin/users', headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 3 # admin_user, user1, user2
    assert any(user['email'] == admin_user.email for user in json_data)
    assert any(user['email'] == user1.email for user in json_data)
    assert any(user['email'] == user2.email for user in json_data)

def test_get_user_by_id_as_admin(client, init_database):
    admin_user = create_admin_user("admin@example.com", "password123")
    user_to_get = create_user("target@example.com", "password123", "Target", "User", "job_seeker")

    login_response = client.post('/api/v1/auth/login', json={
        "email": admin_user.email,
        "password": "password123"
    })
    admin_token = login_response.get_json()['data']['access_token']

    response = client.get(f'/api/v1/admin/users/{user_to_get.id}', headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['email'] == user_to_get.email

def test_get_nonexistent_user_as_admin(client, init_database):
    admin_user = create_admin_user("admin@example.com", "password123")
    login_response = client.post('/api/v1/auth/login', json={
        "email": admin_user.email,
        "password": "password123"
    })
    admin_token = login_response.get_json()['data']['access_token']

    response = client.get(f'/api/v1/admin/users/999', headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 404
    assert response.json['message'] == "User not found"

def test_update_user_role_as_admin(client, init_database):
    admin_user = create_admin_user("admin@example.com", "password123")
    user_to_update = create_user("update@example.com", "password123", "Update", "User", "job_seeker")

    login_response = client.post('/api/v1/auth/login', json={
        "email": admin_user.email,
        "password": "password123"
    })
    admin_token = login_response.get_json()['data']['access_token']

    response = client.put(f'/api/v1/admin/users/{user_to_update.id}/role', json={
        "role": "employer"
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['role'] == "employer"

    # Verify in DB
    updated_user = db.session.get(User, user_to_update.id)
    assert updated_user.role == "employer"

def test_update_user_role_invalid_role_as_admin(client, init_database):
    admin_user = create_admin_user("admin@example.com", "password123")
    user_to_update = create_user("update2@example.com", "password123", "Update2", "User", "job_seeker")

    login_response = client.post('/api/v1/auth/login', json={
        "email": admin_user.email,
        "password": "password123"
    })
    admin_token = login_response.get_json()['data']['access_token']

    response = client.put(f'/api/v1/admin/users/{user_to_update.id}/role', json={
        "role": "invalid_role"
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 400
    assert response.json['message'] == "Invalid role"

def test_update_nonexistent_user_role_as_admin(client, init_database):
    admin_user = create_admin_user("admin@example.com", "password123")
    login_response = client.post('/api/v1/auth/login', json={
        "email": admin_user.email,
        "password": "password123"
    })
    admin_token = login_response.get_json()['data']['access_token']

    response = client.put(f'/api/v1/admin/users/999/role', json={
        "role": "employer"
    }, headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 404
    assert response.json['message'] == "User not found"

def test_delete_user_as_admin(client, init_database):
    admin_user = create_admin_user("admin@example.com", "password123")
    user_to_delete = create_user("delete@example.com", "password123", "Delete", "User", "job_seeker")

    login_response = client.post('/api/v1/auth/login', json={
        "email": admin_user.email,
        "password": "password123"
    })
    admin_token = login_response.get_json()['data']['access_token']

    response = client.delete(f'/api/v1/admin/users/{user_to_delete.id}', headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "User deleted"

    # Verify in DB
    deleted_user = db.session.get(User, user_to_delete.id)
    assert deleted_user is None

def test_delete_nonexistent_user_as_admin(client, init_database):
    admin_user = create_admin_user("admin@example.com", "password123")
    login_response = client.post('/api/v1/auth/login', json={
        "email": admin_user.email,
        "password": "password123"
    })
    admin_token = login_response.get_json()['data']['access_token']

    response = client.delete(f'/api/v1/admin/users/999', headers={
        "Authorization": f"Bearer {admin_token}"
    })
    assert response.status_code == 404
    assert response.json['message'] == "User not found"