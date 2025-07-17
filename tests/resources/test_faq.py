
from app.models.faq import FAQ
from app.extensions import db

def test_create_faq(client):
    print("\n=== Starting test_create_faq ===")
    # Ensure we have a clean state
    with client.application.app_context():
        db.session.query(FAQ).delete()
        db.session.commit()
    
    response = client.post(
        "/api/v1/faqs/",
        json={"question": "Test question?", "answer": "Test answer."},
        headers={"Content-Type": "application/json"}
    )
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == "FAQ created successfully"
    assert json_data['data']['question'] == "Test question?"
    print("=== test_create_faq passed ===\n")

def test_get_faqs(client):
    print("\n=== Starting test_get_faqs ===")
    # Ensure we have a clean state
    with client.application.app_context():
        db.session.query(FAQ).delete()
        db.session.commit()
    
    # First create a FAQ to ensure there's at least one
    client.post(
        "/api/v1/faqs/",
        json={"question": "Test question 2?", "answer": "Test answer 2."},
        headers={"Content-Type": "application/json"}
    )
    
    response = client.get("/api/v1/faqs/")
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "FAQs retrieved"
    assert isinstance(json_data['data'], list)
    assert len(json_data['data']) > 0
    print("=== test_get_faqs passed ===\n")

def test_get_faq(client):
    print("\n=== Starting test_get_faq ===")
    # Ensure we have a clean state
    with client.application.app_context():
        db.session.query(FAQ).delete()
        db.session.commit()
    
    # First create a FAQ to ensure one exists
    response = client.post(
        "/api/v1/faqs/",  # Added trailing slash to match the working test
        json={"question": "Another Test question?", "answer": "Another Test answer.", "category": "General"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Create FAQ response status: {response.status_code}")
    print(f"Create FAQ response data: {response.data}")
    
    json_data = response.get_json()
    if not json_data or 'data' not in json_data or 'id' not in json_data['data']:
        print("Error: Invalid response format from FAQ creation")
        print(f"Response JSON: {json_data}")
        assert False, "Failed to create FAQ for test"
    
    faq_id = json_data['data']['id']
    print(f"Created FAQ with ID: {faq_id}")

    # Now try to get the FAQ
    response = client.get(f"/api/v1/faqs/{faq_id}")
    print(f"Get FAQ response status: {response.status_code}")
    print(f"Get FAQ response data: {response.data}")
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    json_data = response.get_json()
    assert json_data is not None, "Response JSON is None"
    assert 'message' in json_data, "Response missing 'message' field"
    assert 'data' in json_data, "Response missing 'data' field"
    assert json_data['message'] == "FAQ found", f"Unexpected message: {json_data.get('message')}"
    assert json_data['data']['id'] == faq_id, f"FAQ ID mismatch: expected {faq_id}, got {json_data['data'].get('id')}"
    print("=== test_get_faq passed ===\n")

def test_update_faq(client):
    print("\n=== Starting test_update_faq ===")
    # Ensure we have a clean state
    with client.application.app_context():
        db.session.query(FAQ).delete()
        db.session.commit()
    
    # First create a FAQ to ensure one exists
    response = client.post(
        "/api/v1/faqs/",
        json={"question": "Update Test question?", "answer": "Update Test answer.", "category": "General"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Create FAQ response status: {response.status_code}")
    print(f"Create FAQ response data: {response.data}")
    
    json_data = response.get_json()
    if not json_data or 'data' not in json_data or 'id' not in json_data['data']:
        print("Error: Invalid response format from FAQ creation")
        print(f"Response JSON: {json_data}")
        assert False, "Failed to create FAQ for test"
    
    faq_id = json_data['data']['id']
    print(f"Created FAQ with ID: {faq_id}")

    # Now update the FAQ
    update_data = {"question": "Updated question?", "answer": "Updated answer."}
    response = client.patch(
        f"/api/v1/faqs/{faq_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Update FAQ response status: {response.status_code}")
    print(f"Update FAQ response data: {response.data}")
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    json_data = response.get_json()
    assert json_data is not None, "Response JSON is None"
    assert 'message' in json_data, "Response missing 'message' field"
    assert 'data' in json_data, "Response missing 'data' field"
    assert json_data['message'] == "FAQ updated successfully", f"Unexpected message: {json_data.get('message')}"
    assert json_data['data']['question'] == update_data['question'], \
        f"Question not updated. Expected: {update_data['question']}, got: {json_data['data'].get('question')}"
    assert json_data['data']['answer'] == update_data['answer'], \
        f"Answer not updated. Expected: {update_data['answer']}, got: {json_data['data'].get('answer')}"
    
    print("=== test_update_faq passed ===\n")

def test_delete_faq(client):
    print("\n=== Starting test_delete_faq ===")
    # Ensure we have a clean state
    with client.application.app_context():
        db.session.query(FAQ).delete()
        db.session.commit()
    
    # First create a FAQ to ensure one exists
    response = client.post(
        "/api/v1/faqs/",
        json={"question": "Delete Test question?", "answer": "Delete Test answer.", "category": "General"},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Create FAQ response status: {response.status_code}")
    print(f"Create FAQ response data: {response.data}")
    
    json_data = response.get_json()
    if not json_data or 'data' not in json_data or 'id' not in json_data['data']:
        print("Error: Invalid response format from FAQ creation")
        print(f"Response JSON: {json_data}")
        assert False, "Failed to create FAQ for test"
    
    faq_id = json_data['data']['id']
    print(f"Created FAQ with ID: {faq_id}")

    # Now delete the FAQ
    response = client.delete(f"/api/v1/faqs/{faq_id}")
    print(f"Delete FAQ response status: {response.status_code}")
    
    assert response.status_code == 204, f"Expected status code 204, got {response.status_code}"
    
    # Verify the FAQ was actually deleted
    response = client.get(f"/api/v1/faqs/{faq_id}")
    print(f"Verify delete response status: {response.status_code}")
    
    assert response.status_code == 404, f"Expected status code 404 after deletion, got {response.status_code}"
    
    json_data = response.get_json()
    assert json_data is not None, "Response JSON is None"
    assert 'message' in json_data, "Response missing 'message' field"
    assert json_data['message'] == "FAQ not found", f"Unexpected message: {json_data.get('message')}"
    
    print("=== test_delete_faq passed ===\n")
