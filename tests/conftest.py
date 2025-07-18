import os
import pytest
import datetime
from app import create_app, db
from sqlalchemy import create_engine
from config import TestingConfig
from app.models.application import Application
from unittest.mock import patch
from tests.factories import create_user, create_job_posting

os.environ['SENTRY_DSN'] = 'http://public@example.com/1'

@pytest.fixture(scope='function')
def app():
    # Create app with testing config
    app = create_app('testing')
    
    # Create all tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Cleanup
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def cleanup_after_test(app):
    # This will run after each test
    yield
    with app.app_context():
        # Clean up all data from tables
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        db.session.remove()

@pytest.fixture(scope='function')
def init_database(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

        from tests.factories import create_user, create_job_posting

        # Create test users
        user1 = create_user("test1@example.com", "password", "Test", "User1", "job_seeker")
        user2 = create_user("test2@example.com", "password", "Test", "User2", "job_seeker")
        recruiter = create_user("recruiter@example.com", "password", "Test", "Recruiter", "admin")

        # Create test job postings
        job_posting1 = create_job_posting(
            title="Test Job 1",
            description="Description for test job 1",
            location="Test Location 1",
            requirements="Test Requirements 1",
            admin_id=recruiter.id
        )
        job_posting2 = create_job_posting(
            title="Test Job 2",
            description="Description for test job 2",
            location="Test Location 2",
            requirements="Test Requirements 2",
            admin_id=recruiter.id
        )

        yield db
        db.session.remove()
        db.engine.dispose()

@pytest.fixture(scope='function')
def employer(app):
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email="employer@example.com").first()
        if existing_user:
            return existing_user
            
        recruiter = create_user(
            email="employer@example.com",
            password="password",
            first_name="Employer",
            last_name="User",
            role="admin"
        )
        return recruiter

@pytest.fixture(scope='function')
def job_posting(app, employer):
    with app.app_context():
        # Get a fresh employer object within the session
        employer = User.query.get(employer.id)
        
        job = create_job_posting(
            title="Fixture Job",
            description="Description for fixture job",
            location="Test Location",
            requirements="Test Requirements",
            admin_id=employer.id
        )

@pytest.fixture(autouse=True)
def mock_celery_task():
    with patch('app.tasks.email_tasks.send_email_task.delay') as mock_delay:
        yield mock_delay
