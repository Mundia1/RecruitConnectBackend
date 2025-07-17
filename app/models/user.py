from datetime import datetime
from app.extensions import db
from app.extensions import bcrypt
from sqlalchemy_serializer import SerializerMixin

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-password_hash', '-job_postings.admin', '-applications.user', '-feedback.user', '-sent_messages.sender', '-received_messages.receiver')

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # Increased length to 255
    role = db.Column(db.String(50), default='job_seeker') # Enum: job_seeker, admin
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    profile_picture = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
