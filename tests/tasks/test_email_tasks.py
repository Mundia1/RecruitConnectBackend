import pytest
from unittest.mock import patch
from app.tasks.email_tasks import send_email_task
from app import create_app

def test_send_email_task():
    app = create_app('testing')
    with app.app_context():
        with patch('app.tasks.email_tasks.mail.send') as mock_mail_send:
            subject = "Test Subject"
            recipients = ["test@example.com"]
            body = "Test Body"
            send_email_task(subject, recipients, body)
            mock_mail_send.assert_called_once()
