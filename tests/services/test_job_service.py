import pytest
from datetime import datetime, timedelta
from app.services.job_service import JobService
from app.models.job import JobPosting
from app.models.user import User
from app.extensions import db
from werkzeug.exceptions import NotFound

from app import create_app

class TestJobService:
    def setup_method(self):
        self.app = create_app('testing')
    def test_create_job_success(self, init_database):
        """Test successful job creation"""
        # Create a test user (admin)
        with self.app.app_context():
            admin = User(
                email="admin@test.com",
                first_name="Admin",
                last_name="User",
                role="admin"
            )
            admin.set_password("adminpass")
            db.session.add(admin)
            db.session.commit()
            
            # Test data
            job_data = {
                "title": "Senior Developer",
                "description": "Looking for a senior developer with Python experience",
                "location": "Remote",
                "admin_id": admin.id,
                "requirements": "5+ years of Python experience",
                "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
            # Call the service
            job = JobService.create_job(job_data)
        
            # Assertions
            assert job is not None
            assert job.id is not None
            assert job.title == job_data["title"]
            assert job.admin_id == admin.id
            assert isinstance(job.deadline, datetime)
    
    def test_get_job_by_id_success(self, init_database):
        """Test getting a job by ID"""
        with self.app.app_context():
            # Create a test job
            admin = User(email="admin2@test.com", first_name="Admin2")
            admin.set_password("adminpass")
            db.session.add(admin)
            db.session.commit()
            job = JobPosting(
                title="Test Job",
                description="Test Description",
                admin_id=admin.id
            )
            db.session.add(job)
            db.session.commit()
            
            # Get the job
            retrieved_job = JobService.get_job_by_id(job.id)
            
            # Assertions
            assert retrieved_job is not None
            assert retrieved_job.id == job.id
            assert retrieved_job.title == "Test Job"
    
    def test_get_job_by_id_not_found(self, init_database):
        """Test getting a non-existent job by ID"""
        # Test with non-existent ID
        with self.app.app_context():
            with pytest.raises(NotFound) as exc_info:
                JobService.get_job_by_id(99999)
            
            # Assertions
            assert "Job with ID 99999 not found" in str(exc_info.value)
    
    def test_update_job_success(self, init_database):
        """Test updating a job"""
        with self.app.app_context():
            # Create a test job
            admin = User(email="admin3@test.com", first_name="Admin3")
            admin.set_password("adminpass")
            db.session.add(admin)
            db.session.commit()
            job = JobPosting(
                title="Old Title",
                description="Old Description",
                admin_id=admin.id
            )
            db.session.add(job)
            db.session.commit()
            
            # Update data
            update_data = {
                "title": "Updated Title",
                "description": "Updated Description"
            }
            
            # Call the service
            updated_job = JobService.update_job(job.id, update_data)
            
            # Assertions
            assert updated_job.title == "Updated Title"
            assert updated_job.description == "Updated Description"
    
    def test_delete_job_success(self, init_database):
        """Test deleting a job"""
        with self.app.app_context():
            # Create a test job
            admin = User(email="admin4@test.com", first_name="Admin4")
            admin.set_password("adminpass")
            db.session.add(admin)
            db.session.commit()
            job = JobPosting(
                title="Job to Delete",
                description="Will be deleted",
                admin_id=admin.id
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.id
            
            # Call the service
            result = JobService.delete_job(job_id)
            
            # Assertions
            assert result is True
            
            # Verify job is deleted
            with pytest.raises(NotFound):
                JobService.get_job_by_id(job_id)
    
    def test_get_all_jobs(self, init_database):
        """Test getting all jobs"""
        with self.app.app_context():
            # Clear existing jobs
            JobPosting.query.delete()
            
            # Create test jobs
            admin = User(email="admin5@test.com", first_name="Admin5")
            admin.set_password("adminpass")
            db.session.add(admin)
            db.session.commit()
            
            # Create jobs with all required fields
            job1 = JobPosting(
                title="Job 1",
                description="Description 1",
                requirements="Requirements 1",
                location="Location 1",
                admin_id=admin.id,
                deadline=datetime.utcnow() + timedelta(days=30)
            )
            job2 = JobPosting(
                title="Job 2",
                description="Description 2",
                requirements="Requirements 2",
                location="Location 2",
                admin_id=admin.id,
                deadline=datetime.utcnow() + timedelta(days=60)
            )
            db.session.add_all([job1, job2])
            db.session.commit()
            
            # Get all jobs
            jobs = JobService.get_all_jobs()
            
            # Assertions
            assert len(jobs) == 2
            assert any(job.title == "Job 1" for job in jobs)
            assert any(job.title == "Job 2" for job in jobs)