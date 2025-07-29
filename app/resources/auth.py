from flask import Blueprint, request, jsonify
from app.models.user import User
from app.extensions import db, mail
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from flask_mail import Message
import secrets
from datetime import datetime, timedelta

from app.utils.api_response import api_response


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    role = data.get("role", "job_seeker")  # Default to job_seeker

    user = User(
        email=data["email"],
        role=role,
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", "")
        # add other fields as needed
    )
    user.set_password(data["password"])  # <-- Correct way to set password

    db.session.add(user)
    db.session.commit()
    # Return a response (add as needed)
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    print("Login attempt:", data['email'])
    if user:
        print("User found:", user.email, "Role:", user.role)
        print("Password hash:", user.password_hash)
        print("Password correct?", user.check_password(data['password']))
    else:
        print("No user found for email:", data['email'])
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token, "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "profile_picture": getattr(user, "profile_picture", None)
        }}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user:
        try:
            # Generate token and expiry
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            # Send email
            reset_link = f"http://localhost:5173/reset-password/{token}"
            msg = Message("Password Reset Request", recipients=[user.email])
            msg.body = f"Click the link to reset your password: {reset_link}"
            mail.send(msg)
            print("Reset email sent to", user.email)
        except Exception as e:
            print("Failed to send email:", e)
    # Always return the same message for privacy
    return api_response(200, "If the email exists, a reset link has been sent.")

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def set_new_password(token):
    data = request.get_json()
    new_password = data.get("password")
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return api_response(400, "Invalid or expired token")
    user.set_password(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()
    return api_response(200, "Password has been reset successfully")
