import pytest
from app.services.application_service import ApplicationService
from app.models.application import Application
from app.models.user import User
from app.models.job import JobPosting
from app import db
from werkzeug.exceptions import NotFound

def test_create_application(init_database):
    user = init_database.session.query(User).filter_by(email="test1@example.com").first()
    job = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
    assert user is not None
    assert job is not None

    application = ApplicationService.create_application(user.id, job.id)
    init_database.session.commit()
    assert application is not None
    assert application.user_id == user.id
    assert application.job_posting_id == job.id
    assert application.status == "submitted"

    retrieved_application = init_database.session.get(Application, application.id)
    assert retrieved_application is not None
    assert retrieved_application.status == "submitted"

def test_create_application_nonexistent_job(init_database):
    user = init_database.session.query(User).filter_by(email="test1@example.com").first()
    with pytest.raises(NotFound) as exc_info:
        ApplicationService.create_application(user.id, 99999)  # Non-existent job ID
    assert "Cannot create application" in str(exc_info.value)

def test_get_application_by_id(init_database):
    user = init_database.session.query(User).filter_by(email="test1@example.com").first()
    job = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
    created_application = ApplicationService.create_application(user.id, job.id)
    init_database.session.commit()

    retrieved_application = ApplicationService.get_application_by_id(created_application.id)
    assert retrieved_application is not None
    assert retrieved_application.id == created_application.id

def test_get_nonexistent_application(init_database):
    with pytest.raises(NotFound) as exc_info:
        ApplicationService.get_application_by_id(99999)  # Non-existent application ID
    assert "Application with ID 99999 not found" in str(exc_info.value)

def test_get_all_applications(init_database):
    user1 = init_database.session.query(User).filter_by(email="test1@example.com").first()
    user2 = init_database.session.query(User).filter_by(email="test2@example.com").first()
    job1 = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
    job2 = init_database.session.query(JobPosting).filter_by(title="Test Job 2").first()

    # Clear existing applications
    init_database.session.query(Application).delete()
    init_database.session.commit()

    # Create test applications
    ApplicationService.create_application(user1.id, job1.id)
    ApplicationService.create_application(user2.id, job1.id)
    ApplicationService.create_application(user1.id, job2.id)
    init_database.session.commit()

    applications = ApplicationService.get_all_applications()
    assert len(applications) == 3

def test_update_application_status(init_database):
    # Use the existing database session from the fixture
    db = init_database
    
    # Create test data
    user = db.session.query(User).filter_by(email="test1@example.com").first()
    job = db.session.query(JobPosting).filter_by(title="Test Job 1").first()
    
    # Create application
    application = ApplicationService.create_application(user.id, job.id)
    db.session.commit()
    
    try:
        # Update the application status
        updated_application = ApplicationService.update_application_status(
            application.id, "accepted"
        )
        
        # Verify the update
        assert updated_application is not None
        assert updated_application.status == "accepted"
        
        # Refresh from database to verify
        db.session.refresh(updated_application)
        assert updated_application.status == "accepted"
        
    finally:
        # Clean up
        if db.session.is_active:
            db.session.rollback()

def test_update_nonexistent_application(init_database):
    with pytest.raises(NotFound) as exc_info:
        ApplicationService.update_application_status(99999, "accepted")  # Non-existent ID
    assert "Application with ID 99999 not found" in str(exc_info.value)

def test_delete_application(init_database):
    user = init_database.session.query(User).filter_by(email="test1@example.com").first()
    job = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
    created_application = ApplicationService.create_application(user.id, job.id)
    init_database.session.commit()

    result = ApplicationService.delete_application(created_application.id)
    assert result is not None
    assert result.id == created_application.id

    # Verify deletion
    with pytest.raises(NotFound):
        ApplicationService.get_application_by_id(created_application.id)

def test_delete_nonexistent_application(init_database):
    with pytest.raises(NotFound) as exc_info:
        ApplicationService.delete_application(99999)  # Non-existent ID
    assert "Application with ID 99999 not found" in str(exc_info.value)

def test_get_applications_for_user(init_database):
    user1 = init_database.session.query(User).filter_by(email="test1@example.com").first()
    user2 = init_database.session.query(User).filter_by(email="test2@example.com").first()
    job1 = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
    job2 = init_database.session.query(JobPosting).filter_by(title="Test Job 2").first()

    # Clear existing applications
    init_database.session.query(Application).delete()
    init_database.session.commit()

    # Create test applications
    ApplicationService.create_application(user1.id, job1.id)
    ApplicationService.create_application(user2.id, job1.id)
    ApplicationService.create_application(user1.id, job2.id)
    init_database.session.commit()

    user1_applications = ApplicationService.get_applications_for_user(user1.id)
    assert len(user1_applications) == 2

    user2_applications = ApplicationService.get_applications_for_user(user2.id)
    assert len(user2_applications) == 1

def test_get_applications_for_nonexistent_user(init_database):
    applications = ApplicationService.get_applications_for_user(99999)  # Non-existent user ID
    assert len(applications) == 0

def test_get_applications_for_job(init_database):
    user1 = init_database.session.query(User).filter_by(email="test1@example.com").first()
    user2 = init_database.session.query(User).filter_by(email="test2@example.com").first()
    job1 = init_database.session.query(JobPosting).filter_by(title="Test Job 1").first()
    job2 = init_database.session.query(JobPosting).filter_by(title="Test Job 2").first()

    # Clear existing applications
    init_database.session.query(Application).delete()
    init_database.session.commit()

    # Create test applications
    ApplicationService.create_application(user1.id, job1.id)
    ApplicationService.create_application(user2.id, job1.id)
    ApplicationService.create_application(user1.id, job2.id)
    init_database.session.commit()

    job1_applications = ApplicationService.get_applications_for_job(job1.id)
    assert len(job1_applications) == 2

    job2_applications = ApplicationService.get_applications_for_job(job2.id)
    assert len(job2_applications) == 1

def test_get_applications_for_nonexistent_job(init_database):
    applications = ApplicationService.get_applications_for_job(99999)  # Non-existent job ID
    assert len(applications) == 0
