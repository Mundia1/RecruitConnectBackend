from app.models.user import User, db
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

class AuthService:
    @staticmethod
    def register_user(email, password):
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None, "Database error"

        return user, None

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return access_token, user
        return None, None