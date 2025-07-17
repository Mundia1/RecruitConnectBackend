from app.extensions import celery, mail
from flask_mail import Message

@celery.task
def send_email_task(subject, recipients, body):
    msg = Message(subject, recipients=recipients, body=body)
    mail.send(msg)