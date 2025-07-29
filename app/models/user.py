from datetime import datetime, timedelta
from app.extensions import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.dialects import postgresql
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-password_hash', '-job_postings.admin', '-applications.user', '-feedback.user', '-sent_messages.sender', '-received_messages.receiver')

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(postgresql.ENUM('job_seeker', 'employer', 'admin', name='user_role_enum'), default='job_seeker')
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    profile_picture = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reset_token = db.Column(db.String(128), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None
