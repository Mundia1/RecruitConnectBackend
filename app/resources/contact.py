from flask import Blueprint, request, jsonify
from app.schemas.contact import ContactSchema
from app.services.contact_service import ContactService
from app.utils.helpers import api_response

contact_bp = Blueprint('contact', __name__, url_prefix='/contact')
contact_schema = ContactSchema()

@contact_bp.route('/', methods=['POST'])
def send_contact_message():
    data = request.get_json()
    errors = contact_schema.validate(data)
    if errors:
        return api_response(400, "Invalid data", errors)
    
    try:
        result = ContactService.send_contact_message(data)
        return api_response(200, "Contact message sent successfully!", result)
    except Exception as e:
        return api_response(500, "Error sending contact message", str(e))