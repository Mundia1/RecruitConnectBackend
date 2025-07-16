from flask import Blueprint, request, jsonify
from app.schemas.user import UserRegisterSchema, UserLoginSchema, UserSchema
from app.services.auth_service import AuthService
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

user_schema = UserSchema()
register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    errors = register_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    user, error = AuthService.register_user(data['email'], data['password'])
    if error:
        return jsonify({"error": error}), 400

    return user_schema.dump(user), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    errors = login_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    token, user = AuthService.login_user(data['email'], data['password'])
    if not token:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"access_token": token, "user": user_schema.dump(user)})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return user_schema.dump(user)