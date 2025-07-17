from flask import Blueprint, request
from app.schemas.message import MessageSchema
from app.services.message_service import MessageService
from app.utils.helpers import api_response

message_bp = Blueprint('message', __name__, url_prefix='/messages')
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)

@message_bp.route('/', methods=['POST'])
def create_message():
    data = request.get_json()
    errors = message_schema.validate(data)
    if errors:
        return api_response(400, "Invalid data", errors)
    message = MessageService.create_message(data['sender_id'], data['receiver_id'], data['content'])
    return api_response(201, "Message created successfully", message_schema.dump(message))

@message_bp.route('/<int:message_id>', methods=['GET'])
def get_message(message_id):
    message = MessageService.get_message_by_id(message_id)
    if not message:
        return api_response(404, "Message not found")
    return api_response(200, "Message found", message_schema.dump(message))

@message_bp.route('/between/<int:user1_id>/<int:user2_id>', methods=['GET'])
def get_messages_between_users(user1_id, user2_id):
    messages = MessageService.get_messages_between_users(user1_id, user2_id)
    return api_response(200, "Messages retrieved", messages_schema.dump(messages))

@message_bp.route('/<int:message_id>/read', methods=['PATCH'])
def mark_message_as_read(message_id):
    message = MessageService.mark_message_as_read(message_id)
    if not message:
        return api_response(404, "Message not found")
    return api_response(200, "Message marked as read", message_schema.dump(message))

@message_bp.route('/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    result = MessageService.delete_message(message_id)
    if not result:
        return api_response(404, "Message not found")
    return api_response(204, "Message deleted")
