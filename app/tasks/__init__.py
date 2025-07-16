def send_async_email(to, subject, body):
    
    print(f"[Email Task] Sending email to: {to}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return True

def log_task(message):
    
    print(f"[Task Log] {message}")
    return True
