from flask import Blueprint, request
from app.utils.decorators import rate_limit
from app.schemas.user import UserRegisterSchema, UserLoginSchema, UserSchema
from app.services.auth_service import AuthService
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.extensions import db
from app.utils.helpers import api_response

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

user_schema = UserSchema()
register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

@auth_bp.route('/register', methods=['POST'])
@rate_limit("5 per minute")
def register():
    data = request.get_json()
    errors = register_schema.validate(data)
    if errors:
        return api_response(400, "Invalid data", errors)

    user, error = AuthService.register_user(data['email'], data['password'], data['first_name'], data['last_name'])
    if error:
        return api_response(400, error)

    return api_response(201, "User registered successfully", user_schema.dump(user))

@auth_bp.route('/login', methods=['POST'])
@rate_limit("5 per minute")
def login():
    data = request.get_json()
    errors = login_schema.validate(data)
    if errors:
        return api_response(400, "Invalid data", errors)

    access_token, refresh_token, user = AuthService.login_user(data['email'], data['password'])
    if not access_token:
        return api_response(401, "Invalid credentials")

    return api_response(200, "Login successful", {"access_token": access_token, "refresh_token": refresh_token, "user": user_schema.dump(user)})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    return api_response(200, "User found", user_schema.dump(user))

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = AuthService.refresh_access_token(current_user)
    return api_response(200, "Token refreshed", {'access_token': new_access_token})
