import datetime
from app import db
from app.models.user import User
from app.models.job import JobPosting
from app.models.application import Application
from app.models.faq import FAQ
from app.models.feedback import Feedback
from app.models.message import Message

def create_user(email, password, first_name, last_name, role):
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def create_job_posting(title, description, location, requirements, admin_id, deadline=None):
    if deadline is None:
        deadline = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    job_posting = JobPosting(
        title=title,
        description=description,
        location=location,
        requirements=requirements,
        deadline=deadline,
        admin_id=admin_id
    )
    db.session.add(job_posting)
    db.session.commit()
    return job_posting

def create_application(user_id, job_posting_id, status='submitted'):
    application = Application(
        user_id=user_id,
        job_posting_id=job_posting_id,
        status=status
    )
    db.session.add(application)
    db.session.commit()
    return application

def create_faq(question, answer, category=None):
    faq = FAQ(
        question=question,
        answer=answer,
        category=category
    )
    db.session.add(faq)
    db.session.commit()
    return faq

def create_feedback(comment, rating, job_application_id, user_id):
    feedback = Feedback(
        comment=comment,
        rating=rating,
        job_application_id=job_application_id,
        user_id=user_id
    )
    db.session.add(feedback)
    db.session.commit()
    return feedback

def create_message(sender_id, receiver_id, content, application_id=None):
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        application_id=application_id
    )
    db.session.add(message)
    db.session.commit()
    return message
