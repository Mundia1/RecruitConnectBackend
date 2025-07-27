from flask import Blueprint, request, jsonify
from app.models.user import User
from app.extensions import db, jwt
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

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
