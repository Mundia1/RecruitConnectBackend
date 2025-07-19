from app.models.user import User
from app.extensions import db

class AdminService:
    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def get_user_by_id(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def update_user_role(user_id, new_role):
        user = db.session.get(User, user_id)
        if user:
            user.role = new_role
            db.session.commit()
            return user
        return None

    @staticmethod
    def delete_user(user_id):
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
