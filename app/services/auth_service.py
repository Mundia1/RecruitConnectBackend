from app.models.user import User, db
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.exc import IntegrityError
from app.tasks.email_tasks import send_email_task

class AuthService:
    @staticmethod
    def register_user(email, password, first_name, last_name):
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"

        user = User(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
            send_email_task.delay(
                subject="Welcome to RecruitConnect!",
                recipients=[user.email],
                body=f"Dear {user.first_name},\n\nWelcome to RecruitConnect! We are excited to have you on board."
            )
        except IntegrityError:
            db.session.rollback()
            return None, "Database error"

        return user, None

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return access_token, refresh_token, user
        return None, None, None

    @staticmethod
    def refresh_access_token(identity):
        return create_access_token(identity=identity)