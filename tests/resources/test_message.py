
from tests.conftest import client
from app.models.user import User
from app import db

def test_create_message(client, init_database):
    user1 = init_database.session.query(User).filter_by(email="test1@example.com").first()
    user2 = init_database.session.query(User).filter_by(email="test2@example.com").first()

    response = client.post("/api/v1/messages/", json={
        "sender_id": user1.id,
        "receiver_id": user2.id,
        "content": "Test message content."
    })
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == "Message created successfully"
    assert json_data['data']['content'] == "Test message content."

def test_get_message(client, init_database):
    user1 = init_database.session.query(User).filter_by(email="test1@example.com").first()
    user2 = init_database.session.query(User).filter_by(email="test2@example.com").first()

    create_response = client.post("/api/v1/messages/", json={
        "sender_id": user1.id,
        "receiver_id": user2.id,
        "content": "Message to retrieve."
    })
    message_id = create_response.get_json()['data']['id']

    response = client.get(f"/api/v1/messages/{message_id}")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Message found"
    assert json_data['data']['id'] == message_id

def test_get_messages_between_users(client, init_database):
    user1 = init_database.session.query(User).filter_by(email="test1@example.com").first()
    user2 = init_database.session.query(User).filter_by(email="test2@example.com").first()

    client.post("/api/v1/messages/", json={
        "sender_id": user1.id,
        "receiver_id": user2.id,
        "content": "Message 1."
    })
    client.post("/api/v1/messages/", json={
        "sender_id": user2.id,
        "receiver_id": user1.id,
        "content": "Message 2."
    })

    response = client.get(f"/api/v1/messages/between/{user1.id}/{user2.id}")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Messages retrieved"
    assert len(json_data['data']) == 2

def test_mark_message_as_read(client, init_database):
    user1 = init_database.session.query(User).filter_by(email="test1@example.com").first()
    user2 = init_database.session.query(User).filter_by(email="test2@example.com").first()

    create_response = client.post("/api/v1/messages/", json={
        "sender_id": user1.id,
        "receiver_id": user2.id,
        "content": "Message to mark as read."
    })
    message_id = create_response.get_json()['data']['id']

    response = client.patch(f"/api/v1/messages/{message_id}/read")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Message marked as read"
    assert json_data['data']['is_read'] == True

def test_delete_message(client, init_database):
    user1 = init_database.session.query(User).filter_by(email="test1@example.com").first()
    user2 = init_database.session.query(User).filter_by(email="test2@example.com").first()

    create_response = client.post("/api/v1/messages/", json={
        "sender_id": user1.id,
        "receiver_id": user2.id,
        "content": "Message to delete."
    })
    message_id = create_response.get_json()['data']['id']

    response = client.delete(f"/api/v1/messages/{message_id}")
    assert response.status_code == 204
