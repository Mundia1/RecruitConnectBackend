from app import create_app, db
from app.models.user import User
from app.models.job import JobPosting
from app.models.application import Application
from app.models.message import Message
from app.models.feedback import Feedback
from app.models.faq import FAQ
import datetime

def seed_data():
    app = create_app('development')
    with app.app_context():
        print("Seeding database...")

        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create Users
        user1 = User(
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            role="job_seeker",
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        user1.set_password("password123")

        user2 = User(
            email="jane.smith@example.com",
            first_name="Jane",
            last_name="Smith",
            role="job_seeker",
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        user2.set_password("password123")

        admin_user = User(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role="admin",
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        admin_user.set_password("adminpass")

        db.session.add_all([user1, user2, admin_user])
        db.session.commit()
        print("Users created.")

        # Create JobPostings
        job_posting1 = JobPosting(
            title="Software Engineer",
            description="Develop and maintain software applications.",
            location="New York, NY",
            requirements="BS in CS, 3+ years experience",
            deadline=datetime.datetime.utcnow() + datetime.timedelta(days=30),
            posted_at=datetime.datetime.utcnow(),
            admin_id=admin_user.id
        )
        job_posting2 = JobPosting(
            title="Data Scientist",
            description="Analyze complex data sets and build predictive models.",
            location="San Francisco, CA",
            requirements="MS in Data Science, 5+ years experience",
            deadline=datetime.datetime.utcnow() + datetime.timedelta(days=45),
            posted_at=datetime.datetime.utcnow(),
            admin_id=admin_user.id
        )
        db.session.add_all([job_posting1, job_posting2])
        db.session.commit()
        print("JobPostings created.")

        # Create Applications
        application1 = Application(
            user_id=user1.id,
            job_posting_id=job_posting1.id,
            status="submitted",
            applied_at=datetime.datetime.utcnow()
        )
        application2 = Application(
            user_id=user2.id,
            job_posting_id=job_posting1.id,
            status="viewed",
            applied_at=datetime.datetime.utcnow()
        )
        application3 = Application(
            user_id=user1.id,
            job_posting_id=job_posting2.id,
            status="submitted",
            applied_at=datetime.datetime.utcnow()
        )
        db.session.add_all([application1, application2, application3])
        db.session.commit()
        print("Applications created.")

        # Create Messages
        message1 = Message(
            sender_id=user1.id,
            receiver_id=admin_user.id,
            content="Hello, I'm interested in the SE position.",
            sent_at=datetime.datetime.utcnow(),
            is_read=False
        )
        message2 = Message(
            sender_id=admin_user.id,
            receiver_id=user1.id,
            content="Thanks for your interest. We'll review your application.",
            sent_at=datetime.datetime.utcnow(),
            is_read=True
        )
        db.session.add_all([message1, message2])
        db.session.commit()
        print("Messages created.")

        # Create Feedback
        feedback1 = Feedback(
            user_id=admin_user.id,
            job_application_id=application1.id,
            rating=4,
            comment="Good candidate, but lacks experience in X.",
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(feedback1)
        db.session.commit()
        print("Feedback created.")

        # Create FAQs
        faq1 = FAQ(
            question="How do I apply for a job?",
            answer="You can apply by clicking the 'Apply Now' button on any job posting.",
            category="Application Process",
            created_at=datetime.datetime.utcnow()
        )
        faq2 = FAQ(
            question="What is the typical response time for applications?",
            answer="We aim to respond to all applications within 2 weeks.",
            category="Application Process",
            created_at=datetime.datetime.utcnow()
        )
        db.session.add_all([faq1, faq2])
        db.session.commit()
        print("FAQs created.")

        print("Database seeding complete.")

if __name__ == "__main__":
    seed_data()
