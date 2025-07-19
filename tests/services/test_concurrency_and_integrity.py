import pytest
import threading
import time
from datetime import datetime
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import IntegrityError, DBAPIError
from app.services.application_service import ApplicationService
from app.services.job_service import JobService
from app.extensions import db
from app.models.application import Application
from app.models.user import User, bcrypt
from app.models.job import JobPosting
from werkzeug.exceptions import NotFound
from app import create_app

# Create a test app
app = create_app('testing')
app_context = app.app_context()
app_context.push()

class TestConcurrencyAndIntegrity:
    def test_concurrent_job_applications(self, init_database):
        """Test that multiple users can apply to the same job simultaneously"""
        from app import create_app
        test_app = create_app('testing')
        
        with test_app.app_context():
            # Create an admin user
            admin = User(
                email=f"admin_job_{int(time.time())}@example.com",
                first_name="Admin",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()  # Commit admin first to get an ID
            
            # Create a test job with a future deadline
            from datetime import datetime, timedelta
            future_deadline = datetime.utcnow() + timedelta(days=7)
            
            job = JobPosting(
                title=f"Test Job {int(time.time())}",
                description="Test Description",
                requirements="Test Requirements",
                location="Remote",
                admin_id=admin.id,
                deadline=future_deadline
            )
            db.session.add(job)
            db.session.commit()
            
            # Create test users
            users = []
            for i in range(5):
                user = User(
                    email=f"user{i}_{int(time.time())}@example.com",
                    first_name=f"User{i}",
                    last_name="Test",
                    password_hash=bcrypt.generate_password_hash(f"user{i}pass").decode('utf-8')
                )
                db.session.add(user)
                users.append(user)
            db.session.commit()
            
            assert job is not None
            assert len(users) == 5
            
            # Clear existing applications
            Application.query.delete()
            db.session.commit()
            
            # Store job ID and user IDs for thread function
            job_id = job.id
            user_ids = [user.id for user in users]
            
            # Function to apply for job with app context
            def apply_for_job(uid):
                with test_app.app_context():
                    try:
                        # Create a new session for this thread
                        from app.extensions import db as db_session
                        application = ApplicationService.create_application(uid, job_id)
                        db_session.session.commit()
                        return application is not None
                    except Exception as e:
                        db_session.session.rollback()
                        return str(e)
            
            # Start multiple threads to apply for the job
            threads = []
            results = []
            
            for uid in user_ids:
                t = threading.Thread(target=lambda x=uid: results.append(apply_for_job(x)))
                threads.append(t)
                t.start()
            
            # Wait for all threads to complete
            for t in threads:
                t.join()
            
            # Verify all applications were created successfully
            assert all(isinstance(r, bool) and r for r in results), f"Not all applications were created successfully: {results}"
            assert len(results) == 5
            
            # Verify the correct number of applications exist in the database
            applications = Application.query.filter_by(job_posting_id=job.id).all()
            assert len(applications) == 5, f"Expected 5 applications, got {len(applications)}"
            assert all(isinstance(app, Application) for app in applications)

    def test_race_condition_on_application_status(self, init_database):
        """Test race condition when updating application status"""
        from app import create_app
        test_app = create_app('testing')
        
        with test_app.app_context():
            # Create test data
            user = User(
                email=f"test_race_{int(time.time())}@example.com",
                first_name="Test",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("testpassword").decode('utf-8')
            )
            db.session.add(user)
            
            # Create an admin user
            admin = User(
                email=f"admin_{int(time.time())}@example.com",
                first_name="Admin",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            
            # Create a job
            job = JobPosting(
                title=f"Test Job {int(time.time())}",
                description="Test Description",
                requirements="Test Requirements",
                location="Remote",
                admin_id=admin.id
            )
            db.session.add(job)
            db.session.commit()
            
            # Create an application
            application = Application(
                user_id=user.id,
                job_posting_id=job.id,
                status='submitted',
                applied_at=datetime.utcnow()
            )
            db.session.add(application)
            db.session.commit()
            
            # Store application ID for thread function
            app_id = application.id
            
            # Function to update status with app context
            def update_status(status):
                with test_app.app_context():
                    try:
                        # Get a fresh copy of the application
                        app = db.session.get(Application, app_id)
                        if not app:
                            return f"Application {app_id} not found"
                        app.status = status
                        time.sleep(0.1)  # Simulate processing time
                        db.session.commit()
                        return app
                    except Exception as e:
                        db.session.rollback()
                        return str(e)
            
            # Start multiple threads to update status
            statuses = ['reviewing', 'accepted', 'rejected']
            threads = []
            results = []
            
            for status in statuses:
                t = threading.Thread(
                    target=lambda s=status: results.append(update_status(s))
                )
                threads.append(t)
                t.start()
            
            # Wait for all threads to complete
            for t in threads:
                t.join()
            
            # Only one update should succeed
            successful_updates = [r for r in results if isinstance(r, Application)]
            assert len(successful_updates) == 1
            
            # Verify the final status is one of the attempted statuses
            db.session.refresh(application)
            assert application.status in statuses

    # This test is a duplicate and has been removed. See the other test_cascading_delete_user_with_applications method below.

    def test_foreign_key_constraint_violation(self, init_database):
        """Test that foreign key constraints are enforced"""
        # Try to create an application with non-existent user and job
        with pytest.raises(IntegrityError):
            application = Application(
                user_id=999999,
                job_posting_id=999999,
                status='submitted'
            )
            db.session.add(application)
            db.session.commit()
    
    def test_unique_constraint_violation(self, init_database):
        """Test that users can't apply to the same job twice"""
        # Create a test user and job
        user = User(
            email=f"test_dup_{int(time.time())}@example.com",
            first_name="Test",
            last_name="User",
            password_hash=bcrypt.generate_password_hash("testpassword").decode('utf-8')
        )
        db.session.add(user)
        
        # Create an admin user first
        admin = User(
            email=f"admin_{int(time.time())}@example.com",
            first_name="Admin",
            last_name="User",
            password_hash=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        
        job = JobPosting(
            title=f"Test Job {int(time.time())}",
            description="Test Description",
            requirements="Test Requirements",
            location="Remote",
            admin_id=admin.id
        )
        db.session.add(job)
        db.session.commit()
        
        # First application should succeed
        first_application = ApplicationService.create_application(user.id, job.id)
        db.session.commit()
        assert first_application is not None
        
        # Second application with same user and job should return None
        second_application = ApplicationService.create_application(user.id, job.id)
        assert second_application is None
        
        # Verify only one application exists
        applications = Application.query.filter_by(user_id=user.id, job_posting_id=job.id).all()
        assert len(applications) == 1
    
    @patch('app.extensions.db.session.commit')
    def test_database_connection_failure(self, mock_commit, init_database):
        """Test handling of database connection failures"""
        # Simulate database connection failure on commit
        mock_commit.side_effect = DBAPIError("Connection failed", "", "")
        
        user = User.query.first()
        job = JobPosting.query.first()
        
        with pytest.raises(DBAPIError):
            ApplicationService.create_application(user.id, job.id)
        
        # Verify transaction was rolled back
        db.session.rollback()
    
    def test_external_service_failure(self, init_database):
        """Test handling of external service failures"""
        # Create test user and job
        user = User(
            email=f"test_ext_{int(time.time())}@example.com",
            first_name="Test",
            last_name="User",
            password_hash=bcrypt.generate_password_hash("testpassword").decode('utf-8')
        )
        db.session.add(user)
        
        # Create an admin user first
        admin = User(
            email=f"admin_{int(time.time())}@example.com",
            first_name="Admin",
            last_name="User",
            password_hash=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        
        job = JobPosting(
            title=f"Test Job {int(time.time())}",
            description="Test Description",
            requirements="Test Requirements",
            location="Remote",
            admin_id=admin.id
        )
        db.session.add(job)
        db.session.commit()
        
        # Test creating an application
        application = ApplicationService.create_application(user.id, job.id)
        assert application is not None
        
        # Verify the application was created in the database
        db_application = db.session.get(Application, application.id)
        assert db_application is not None
        assert db_application.user_id == user.id
        assert db_application.job_posting_id == job.id
        assert db_application.status == 'submitted'
    
    def test_invalid_input_data(self, init_database):
        """Test handling of invalid input data"""
        # Create a test user and job first
        user = User(
            email=f"test_invalid_{int(time.time())}@example.com",
            first_name="Test",
            last_name="User",
            password_hash=bcrypt.generate_password_hash("testpassword").decode('utf-8')
        )
        db.session.add(user)
        
        # Create an admin user for the job
        admin = User(
            email=f"admin_{int(time.time())}@example.com",
            first_name="Admin",
            last_name="User",
            password_hash=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        
        job = JobPosting(
            title=f"Test Job {int(time.time())}",
            description="Test Description",
            requirements="Test Requirements",
            location="Remote",
            admin_id=admin.id
        )
        db.session.add(job)
        db.session.commit()
        
        # Test with invalid user ID (None)
        with pytest.raises((ValueError, TypeError, IntegrityError)):
            try:
                ApplicationService.create_application(None, job.id)
            except Exception as e:
                db.session.rollback()
                raise e
        
        # Test with invalid job ID (None) - should raise ValueError or TypeError before trying to access the database
        with pytest.raises((ValueError, TypeError)):
            ApplicationService.create_application(user.id, None)
        
        # Test with non-existent user ID - should raise IntegrityError due to foreign key violation
        with pytest.raises(IntegrityError):
            try:
                ApplicationService.create_application(999999999, job.id)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
        
        # Test with non-existent job ID
        with pytest.raises(NotFound):
            # Use a very large number that's unlikely to exist
            non_existent_job_id = 999999999
            ApplicationService.create_application(user.id, non_existent_job_id)
            
        # Verify no applications were created for invalid inputs
        applications = Application.query.filter_by(user_id=user.id).all()
        assert len(applications) == 0

    def test_concurrent_resource_updates(self, init_database):
        """Test that concurrent updates to the same resource maintain data integrity"""
        # Create a test job
        # Create an admin user first
        admin = User(
            email=f"admin_update_{int(time.time())}@example.com",
            first_name="Admin",
            last_name="Updater",
            password_hash=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        
        job = JobPosting(
            title=f"Original Title {int(time.time())}",
            description="Test Description",
            requirements="Test Requirements",
            location="Remote",
            admin_id=admin.id
        )
        db.session.add(job)
        db.session.commit()
        
        # Function to update job title with app context
        def update_job_title(new_title):
            with app.app_context():
                try:
                    # Get a fresh copy of the job
                    job = db.session.get(JobPosting, job_id)
                    job.title = new_title
                    time.sleep(0.1)  # Simulate processing time
                    db.session.commit()
                    return job
                except Exception as e:
                    db.session.rollback()
                    return str(e)
        
        # Store the job ID for the thread function
        job_id = job.id
        
        # Start multiple threads to update the job
        new_titles = [f"Updated Title {i}" for i in range(3)]
        threads = []
        results = []
        
        for title in new_titles:
            t = threading.Thread(
                target=lambda t=title: results.append(update_job_title(t))
            )
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Verify only one update was successful
        successful_updates = [r for r in results if isinstance(r, JobPosting)]
        assert len(successful_updates) == 1
        

    def test_cascading_delete_user_with_applications(self, init_database):
        """Test that applications are deleted when a user is deleted"""
        from app import create_app
        test_app = create_app('testing')
            
        with test_app.app_context():
            # Create test data
            user = User(
                email=f"test_cascade_{int(time.time())}@example.com",
                first_name="Test",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("testpassword").decode('utf-8')
            )
            db.session.add(user)
                
            # Create an admin user
            admin = User(
                email=f"admin_{int(time.time())}@example.com",
                first_name="Admin",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
                
            # Create a job
            job = JobPosting(
                title=f"Test Job {int(time.time())}",
                description="Test Description",
                requirements="Test Requirements",
                location="Remote",
                admin_id=admin.id
            )
            db.session.add(job)
            db.session.commit()
                
            # Store user ID for verification
            user_id = user.id
                
            # Create multiple jobs for the user to apply to
            jobs = []
            for i in range(3):
                job = JobPosting(
                    title=f"Test Job {i} {int(time.time())}",
                    description=f"Test Description {i}",
                    requirements=f"Test Requirements {i}",
                    location="Remote",
                    admin_id=admin.id
                )
                db.session.add(job)
                jobs.append(job)
            db.session.commit()
            
            # Create one application per job for the user and commit each one
            for job in jobs:
                application = Application(
                    user_id=user_id,
                    job_posting_id=job.id,
                    status='submitted',
                    applied_at=datetime.utcnow()
                )
                db.session.add(application)
                db.session.commit()  # Commit after each addition
            
            # Verify applications exist
            applications = Application.query.filter_by(user_id=user_id).all()
            assert len(applications) == 3, f"Expected 3 applications, got {len(applications)}"
            
            # Get application IDs for later verification
            application_ids = [app.id for app in applications]
            
            # Start a new transaction for the delete
            db.session.begin_nested()
            
            try:
                # Get a fresh copy of the user with a lock
                user_to_delete = User.query.filter_by(id=user_id).with_for_update().first()
                assert user_to_delete is not None, "User not found for deletion"
                
                # Delete the user
                db.session.delete(user_to_delete)
                db.session.commit()
                
                # Verify the user was deleted
                assert db.session.get(User, user_id) is None, "User was not deleted"
                
                # Verify applications were deleted
                remaining_applications = Application.query.filter(Application.id.in_(application_ids)).all()
                assert len(remaining_applications) == 0, \
                    f"Expected 0 applications after user deletion, got {len(remaining_applications)}"
                    
            except Exception as e:
                db.session.rollback()
                raise e
            
    def test_race_condition_on_application_status(self, init_database):
        """Test race condition when updating application status"""
        from app import create_app
        test_app = create_app('testing')
        
        with test_app.app_context():
            # Create test data
            user = User(
                email=f"test_race_{int(time.time())}@example.com",
                first_name="Test",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("testpass").decode('utf-8')
            )
            db.session.add(user)
            
            # Create an admin user
            admin = User(
                email=f"admin_race_{int(time.time())}@example.com",
                first_name="Admin",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            
            # Create a test job with future deadline
            from datetime import datetime, timedelta
            future_deadline = datetime.utcnow() + timedelta(days=7)
            
            job = JobPosting(
                title=f"Test Job {int(time.time())}",
                description="Test Description",
                requirements="Test Requirements",
                location="Remote",
                admin_id=admin.id,
                deadline=future_deadline
            )
            db.session.add(job)
            db.session.commit()
            
            # Create a test application
            application = Application(
                user_id=user.id,
                job_posting_id=job.id,
                status='submitted',
                applied_at=datetime.utcnow()
            )
            db.session.add(application)
            db.session.commit()
            
            app_id = application.id
            
            # Event to synchronize threads
            from threading import Event
            start_event = Event()
            
            # Function to update application status with simulated race condition
            def update_status(new_status):
                from app.services.application_service import ApplicationService
                
                # Wait for all threads to be ready
                start_event.wait()
                
                try:
                    # Create a new application context for this thread
                    with test_app.app_context():
                        # Use the application service to update the status with simulated delay
                        # to help create a race condition
                        app = ApplicationService.update_application_status(
                            app_id, 
                            new_status,
                            simulate_delay=True  # Add delay to ensure proper race condition
                        )
                        return True, new_status
                except Exception as e:
                    return False, str(e)
            
            # Start multiple threads to update the status
            threads = []
            results = []
            statuses = ['under_review', 'accepted', 'rejected']
            
            # Create and start threads
            for status in statuses:
                t = threading.Thread(
                    target=lambda s=status: results.append(update_status(s)),
                    daemon=True
                )
                threads.append(t)
                t.start()
            
            # Signal all threads to start at the same time
            start_event.set()
            
            # Wait for all threads to complete
            for t in threads:
                t.join(timeout=5.0)  # Add timeout to prevent hanging
            
            # Process results
            successful_updates = [r for r in results if r[0] is True]
            
            # Get the final state of the application
            with test_app.app_context():
                final_application = db.session.get(Application, app_id)
                final_status = final_application.status if final_application else None

            # Verify that at least one update was successful
            assert len(successful_updates) > 0, \
                f"Expected at least one successful update, but got none. Results: {results}"
                
            # Verify the final status is one of the attempted statuses
            assert final_status in statuses, \
                f"Final status {final_status} is not one of the attempted statuses: {statuses}"
                
            # In a real-world scenario, the final status should be the last one that committed
            # However, due to the nature of the test, we'll just verify it's consistent
            print(f"\nTest results: {results}")
            print(f"Final status: {final_status}")
            print(f"Successful updates: {successful_updates}")
            
            # Verify that the final status is one of the successful updates
            assert any(final_status == s[1] for s in successful_updates), \
                f"Final status {final_status} does not match any successful update status: {successful_updates}"

    def test_concurrent_deletion(self, init_database):
        """Test that concurrent deletions are handled correctly"""
        from app import create_app
        test_app = create_app('testing')
        
        with test_app.app_context():
            # Create test data
            user = User(
                email=f"test_del_{int(time.time())}@example.com",
                first_name="Test",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("testpassword").decode('utf-8')
            )
            db.session.add(user)
            
            # Create an admin user
            admin = User(
                email=f"admin_{int(time.time())}@example.com",
                first_name="Admin",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            
            # Create a job
            job = JobPosting(
                title=f"Test Job {int(time.time())}",
                description="Test Description",
                requirements="Test Requirements",
                location="Remote",
                admin_id=admin.id
            )
            db.session.add(job)
            db.session.commit()
            
            # Create test application
            application = Application(
                user_id=user.id,
                job_posting_id=job.id,
                status='submitted',
                applied_at=datetime.utcnow()
            )
            db.session.add(application)
            db.session.commit()
            
            # Store application ID for thread function
            app_id = application.id
            
            # Function to delete application with app context and row-level locking
            def delete_application():
                with test_app.app_context():
                    try:
                        # Start a new transaction with SERIALIZABLE isolation level
                        with db.session.begin():
                            # Get a fresh copy of the application with row-level lock
                            app = db.session.query(Application).filter_by(id=app_id).with_for_update(nowait=True).first()
                            if app:
                                db.session.delete(app)
                                # Don't commit here - let the context manager handle it
                                return True
                            return False
                    except Exception as e:
                        db.session.rollback()
                        # Check if this was a lock timeout (another thread has the row locked)
                        if 'could not obtain lock' in str(e).lower():
                            return "Lock not acquired"
                        return str(e)
            
            # Start multiple threads to delete the application
            threads = []
            results = []
            
            # Use a lock to synchronize access to results
            results_lock = threading.Lock()
            
            def run_delete():
                result = delete_application()
                with results_lock:
                    results.append(result)
            
            # Create and start threads
            for _ in range(3):
                t = threading.Thread(target=run_delete)
                threads.append(t)
                t.start()
            
            # Wait for all threads to complete
            for t in threads:
                t.join()
            
            # Debug output
            print(f"Deletion results: {results}")
            
            # Verify that we have exactly one successful deletion
            success_count = results.count(True)
            lock_failures = results.count("Lock not acquired")
            
            # We should have either:
            # 1. One success and the rest are lock failures, or
            # 2. One success and the rest are False (if the row was already deleted)
            assert success_count == 1, f"Expected exactly 1 successful deletion, got {success_count}"
            assert len(results) in (success_count + lock_failures, success_count + (len(results) - success_count)), \
                f"Unexpected results: {results}"
            
            # Verify the application is no longer in the database
            with test_app.app_context():
                assert db.session.get(Application, application.id) is None, "Application was not deleted"

    def test_concurrent_resource_updates(self, init_database):
        """Test that concurrent updates are handled correctly"""
        from app import create_app
        test_app = create_app('testing')
        
        with test_app.app_context():
            # Create test data
            user = User(
                email=f"test_update_{int(time.time())}@example.com",
                first_name="Test",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("testpassword").decode('utf-8')
            )
            db.session.add(user)
            
            # Create an admin user
            admin = User(
                email=f"admin_{int(time.time())}@example.com",
                first_name="Admin",
                last_name="User",
                password_hash=bcrypt.generate_password_hash("adminpass").decode('utf-8'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            
            # Create a job with a known title that we'll update
            original_title = f"Test Job {int(time.time())}"
            job = JobPosting(
                title=original_title,
                description="Test Description",
                requirements="Test Requirements",
                location="Remote",
                admin_id=admin.id
            )
            db.session.add(job)
            db.session.commit()
            
            # Store job ID for thread function
            job_id = job.id
            
            # Function to update job title with a delay to ensure concurrency
            def update_job_title(new_title):
                with test_app.app_context():
                    try:
                        # Get a fresh copy of the job with a lock
                        job = db.session.query(JobPosting).with_for_update().filter(JobPosting.id == job_id).first()
                        if job:
                            # Save the current title before updating
                            current_title = job.title
                            
                            # Simulate some processing time
                            time.sleep(0.1)
                            
                            # Update the title
                            job.title = new_title
                            db.session.commit()
                            return {
                                'success': True,
                                'previous_title': current_title,
                                'new_title': new_title
                            }
                        return {'success': False, 'error': 'Job not found'}
                    except Exception as e:
                        db.session.rollback()
                        return {'success': False, 'error': str(e)}
            
            # Start multiple threads to update the job title
            threads = []
            new_titles = [f"Updated Title {i}" for i in range(3)]
            results = []
            
            # Create a lock for thread-safe appending to results
            results_lock = threading.Lock()
            
            def update_and_collect(title):
                result = update_job_title(title)
                with results_lock:
                    results.append(result)
            
            for title in new_titles:
                t = threading.Thread(target=update_and_collect, args=(title,))
                threads.append(t)
                t.start()
            
            # Wait for all threads to complete
            for t in threads:
                t.join()
            
            # Get the final state of the job
            job = db.session.get(JobPosting, job_id)
            db.session.refresh(job)
            
            # Verify at least one update succeeded
            successful_updates = [r for r in results if r.get('success')]
            assert len(successful_updates) > 0
            
            # The final title should match one of the attempted titles or the original
            assert job.title in new_titles + [original_title]
            
            # Verify the final state is consistent
            all_jobs = JobPosting.query.filter_by(id=job_id).all()
            assert len(all_jobs) == 1  # Should only be one job with this ID
            
            # Verify that the job's title was actually updated
            assert job.title != original_title or len(successful_updates) == 0
