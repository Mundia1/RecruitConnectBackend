
from tests.conftest import client
from app.models.user import User
from app.models.application import Application
from app.models.job import JobPosting

def test_create_feedback(client, init_database):
    user = init_database.session.query(User).filter_by(email="test1@example.com").first()
    job_posting = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
    application = Application(user_id=user.id, job_posting_id=job_posting.id)
    init_database.session.add(application)
    init_database.session.commit()

    response = client.post("/api/v1/feedback/", json={
        "user_id": user.id,
        "job_application_id": application.id,
        "rating": 5,
        "comment": "Great feedback!"
    })
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == "Feedback created successfully"
    assert json_data['data']['rating'] == 5

def test_get_feedbacks_for_application(client, init_database):
    # Get test data
    from app.extensions import db
    from app.models.feedback import Feedback
    
    # Create test data directly
    with client.application.app_context():
        user = User.query.filter_by(email="test1@example.com").first()
        job_posting = JobPosting.query.filter_by(title="Test Job 1").first()
        
        # Create application
        application = Application(user_id=user.id, job_posting_id=job_posting.id)
        db.session.add(application)
        db.session.commit()
        
        # Create feedback
        feedback = Feedback(
            user_id=user.id,
            job_application_id=application.id,
            rating=4,
            comment="Good feedback!"
        )
        db.session.add(feedback)
        db.session.commit()
        
        # Verify feedback was created
        feedbacks = Feedback.query.filter_by(job_application_id=application.id).all()
        print(f"Created feedbacks: {len(feedbacks)}")
        for f in feedbacks:
            print(f"Feedback: {f.id}, Application: {f.job_application_id}, User: {f.user_id}")
        
        # Store application ID for the test
        app_id = application.id
    
    # Test API endpoint
    response = client.get(f"/api/v1/feedback/application/{app_id}")
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    json_data = response.get_json()
    assert json_data is not None, "Response JSON is None"
    assert 'message' in json_data, f"Response missing 'message' field: {json_data}"
    assert 'data' in json_data, f"Response missing 'data' field: {json_data}"
    assert json_data['message'] == "Feedbacks retrieved", f"Unexpected message: {json_data.get('message')}"
    assert len(json_data['data']) > 0, f"Expected at least one feedback, got {len(json_data.get('data', []))}"

def test_get_feedback(client, init_database):
    # Get test data
    from app.extensions import db
    from app.models.feedback import Feedback
    
    # Create test data directly
    with client.application.app_context():
        user = User.query.filter_by(email="test1@example.com").first()
        job_posting = JobPosting.query.filter_by(title="Test Job 1").first()
        
        # Create application
        application = Application(user_id=user.id, job_posting_id=job_posting.id)
        db.session.add(application)
        db.session.commit()
        
        # Create feedback directly to ensure it's in the database
        feedback = Feedback(
            user_id=user.id,
            job_application_id=application.id,
            rating=3,
            comment="Okay feedback!"
        )
        db.session.add(feedback)
        db.session.commit()
        
        # Store feedback ID for the test
        feedback_id = feedback.id
        print(f"Created feedback with ID: {feedback_id}")
    
    # Test API endpoint
    response = client.get(f"/api/v1/feedback/{feedback_id}")
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    json_data = response.get_json()
    assert json_data is not None, "Response JSON is None"
    assert 'message' in json_data, f"Response missing 'message' field: {json_data}"
    assert 'data' in json_data, f"Response missing 'data' field: {json_data}"
    assert json_data['message'] == "Feedback found", f"Unexpected message: {json_data.get('message')}"
    assert json_data['data']['id'] == feedback_id, f"Unexpected feedback ID: expected {feedback_id}, got {json_data['data'].get('id')}"

def test_update_feedback(client, init_database):
    # Get test data
    from app.extensions import db
    from app.models.feedback import Feedback
    
    # Create test data directly
    with client.application.app_context():
        user = User.query.filter_by(email="test1@example.com").first()
        job_posting = JobPosting.query.filter_by(title="Test Job 1").first()
        
        # Create application
        application = Application(user_id=user.id, job_posting_id=job_posting.id)
        db.session.add(application)
        db.session.commit()
        
        # Create feedback directly to ensure it's in the database
        feedback = Feedback(
            user_id=user.id,
            job_application_id=application.id,
            rating=3,
            comment="Initial feedback"
        )
        db.session.add(feedback)
        db.session.commit()
        
        # Store feedback ID for the test
        feedback_id = feedback.id
        print(f"Created feedback with ID: {feedback_id}")
    
    # Test API endpoint
    update_data = {"rating": 4, "comment": "Updated feedback"}
    response = client.patch(
        f"/api/v1/feedback/{feedback_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Update response status: {response.status_code}")
    print(f"Update response data: {response.data}")
    
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    json_data = response.get_json()
    assert json_data is not None, "Response JSON is None"
    assert 'message' in json_data, f"Response missing 'message' field: {json_data}"
    assert 'data' in json_data, f"Response missing 'data' field: {json_data}"
    assert json_data['message'] == "Feedback updated successfully", f"Unexpected message: {json_data.get('message')}"
    assert json_data['data']['rating'] == update_data['rating'], f"Rating not updated. Expected {update_data['rating']}, got {json_data['data'].get('rating')}"
    assert json_data['data']['comment'] == update_data['comment'], f"Comment not updated. Expected {update_data['comment']}, got {json_data['data'].get('comment')}"

def test_delete_feedback(client, init_database):
    # Get test data
    from app.extensions import db
    from app.models.feedback import Feedback
    
    # Create test data directly
    with client.application.app_context():
        user = User.query.filter_by(email="test1@example.com").first()
        job_posting = JobPosting.query.filter_by(title="Test Job 1").first()
        
        # Create application
        application = Application(user_id=user.id, job_posting_id=job_posting.id)
        db.session.add(application)
        db.session.commit()
        
        # Create feedback directly to ensure it's in the database
        feedback = Feedback(
            user_id=user.id,
            job_application_id=application.id,
            rating=5,
            comment="Delete this feedback!"
        )
        db.session.add(feedback)
        db.session.commit()
        
        # Store feedback ID for the test
        feedback_id = feedback.id
        print(f"Created feedback with ID: {feedback_id}")
    
    # Test API endpoint
    response = client.delete(f"/api/v1/feedback/{feedback_id}")
    assert response.status_code == 204
    
    # Verify feedback is deleted
    verify_response = client.get(f"/api/v1/feedback/{feedback_id}")
    print(f"Verify delete response status: {verify_response.status_code}")
    assert verify_response.status_code == 404
