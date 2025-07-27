import os
import pytest
import datetime
from app import create_app, db
from sqlalchemy import create_engine
from config import TestingConfig
from app.models.application import Application
from app.models.user import User  # Add this import
from app.models.job import JobPosting  # Add this import
from unittest.mock import patch
from tests.factories import create_user, create_job_posting

os.environ['SENTRY_DSN'] = 'http://public@example.com/1'

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
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
        db.session.begin(subtransactions=True)
        yield db
        db.session.rollback()
        db.session.close()

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
        # Ensure employer is in the current session
        employer = db.session.merge(employer)
        
        # Create and return a job posting
        job = create_job_posting(
            title="Fixture Job",
            description="Description for fixture job",
            location="Test Location",
            requirements="Test Requirements",
            admin_id=employer.id,
            deadline=datetime.datetime.utcnow() + datetime.timedelta(days=30)
        )
        return job

@pytest.fixture(autouse=True)
def mock_celery_task():
    with patch('app.tasks.email_tasks.send_email_task.delay') as mock_delay:
        yield mock_delay
