from flask import Blueprint, jsonify, request
from app.services.admin_service import AdminService
from app.schemas.user import UserSchema
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    users = AdminService.get_all_users()
    return UserSchema(many=True).dump(users), 200

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = AdminService.get_user_by_id(user_id)
    if user:
        return UserSchema().dump(user), 200
    return jsonify({'message': 'User not found'}), 404

@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id):
    data = request.get_json()
    new_role = data.get('role')
    if not new_role or new_role not in ['job_seeker', 'employer', 'admin']:
        return jsonify({'message': 'Invalid role'}), 400
    user = AdminService.update_user_role(user_id, new_role)
    if user:
        return UserSchema().dump(user), 200
    return jsonify({'message': 'User not found'}), 404

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    if AdminService.delete_user(user_id):
        return jsonify({'message': 'User deleted'}), 200
    return jsonify({'message': 'User not found'}), 404
