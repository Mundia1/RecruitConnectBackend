import os
import pytest
import datetime
from app import create_app, db
from sqlalchemy import create_engine
from config import TestingConfig
from app.models.user import User
from app.models.job import JobPosting
from app.models.application import Application
from unittest.mock import patch

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

        # Create test users
        user1 = User(
            email="test1@example.com",
            first_name="Test",
            last_name="User1",
            role="job_seeker"
        )
        user1.set_password("password")

        user2 = User(
            email="test2@example.com",
            first_name="Test",
            last_name="User2",
            role="job_seeker"
        )
        user2.set_password("password")

        recruiter = User(
            email="recruiter@example.com",
            first_name="Test",
            last_name="Recruiter",
            role="admin"
        )
        recruiter.set_password("password")

        db.session.add_all([user1, user2, recruiter])
        db.session.commit()

        # Create test job postings
        job_posting1 = JobPosting(
            title="Test Job 1",
            description="Description for test job 1",
            location="Test Location 1",
            requirements="Test Requirements 1",
            deadline=datetime.datetime.utcnow() + datetime.timedelta(days=10),
            admin_id=recruiter.id
        )
        job_posting2 = JobPosting(
            title="Test Job 2",
            description="Description for test job 2",
            location="Test Location 2",
            requirements="Test Requirements 2",
            deadline=datetime.datetime.utcnow() + datetime.timedelta(days=20),
            admin_id=recruiter.id
        )
        db.session.add_all([job_posting1, job_posting2])
        db.session.commit()

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
            
        recruiter = User(
            email="employer@example.com",
            first_name="Employer",
            last_name="User",
            role="admin"
        )
        recruiter.set_password("password")
        db.session.add(recruiter)
        db.session.commit()
        return recruiter

@pytest.fixture(scope='function')
def job_posting(app, employer):
    with app.app_context():
        # Get a fresh employer object within the session
        employer = User.query.get(employer.id)
        
        job = JobPosting(
            title="Fixture Job",
            description="Description for fixture job",
            location="Test Location",
            requirements="Test Requirements",
            deadline=datetime.datetime.utcnow() + datetime.timedelta(days=30),
            admin_id=employer.id
        )
        db.session.add(job)
        db.session.commit()
        return job

@pytest.fixture(autouse=True)
def mock_celery_task():
    with patch('app.tasks.email_tasks.send_email_task.delay') as mock_delay:
        yield mock_delay
