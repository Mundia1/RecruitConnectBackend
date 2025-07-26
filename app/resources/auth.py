from flask import Blueprint, request, jsonify
from app.models.user import User
from app.extensions import db, jwt
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
=======
user_schema = UserSchema()
register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
@rate_limit("5 per minute")
def register():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    user = User(
        email=data['email'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        role=data.get('role', 'job_seeker')
    )
    user.set_password(data['password'])
    db.session.add(user)
    try:
        db.session.commit()
        return jsonify({"message": "User created"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email already exists"}), 400

@auth_bp.route('/login', methods=['POST'])

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
@rate_limit("5 per minute")

def login():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token, "user": user.email}), 200
    return jsonify({"message": "Invalid credentials"}), 401
