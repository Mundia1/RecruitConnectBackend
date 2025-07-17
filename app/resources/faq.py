from flask import Blueprint, request
from app.schemas.faq import FAQSchema
from app.services.faq_service import FAQService
from app.utils.helpers import api_response

faq_bp = Blueprint('faq', __name__, url_prefix='/faqs')
faq_schema = FAQSchema()
faqs_schema = FAQSchema(many=True)

@faq_bp.route('/', methods=['POST'])
def create_faq():
    data = request.get_json()
    errors = faq_schema.validate(data)
    if errors:
        return api_response(400, "Invalid data", errors)
    faq = FAQService.create_faq(data['question'], data['answer'], data.get('category'))
    return api_response(201, "FAQ created successfully", faq_schema.dump(faq))

@faq_bp.route('/<int:faq_id>', methods=['GET'])
def get_faq(faq_id):
    faq = FAQService.get_faq_by_id(faq_id)
    if not faq:
        return api_response(404, "FAQ not found")
    return api_response(200, "FAQ found", faq_schema.dump(faq))

@faq_bp.route('/', methods=['GET'])
def get_all_faqs():
    faqs = FAQService.get_all_faqs()
    return api_response(200, "FAQs retrieved", faqs_schema.dump(faqs))

@faq_bp.route('/<int:faq_id>', methods=['PATCH'])
def update_faq(faq_id):
    data = request.get_json()
    errors = faq_schema.validate(data, partial=True)
    if errors:
        return api_response(400, "Invalid data", errors)
    faq = FAQService.update_faq(faq_id, data.get('question'), data.get('answer'), data.get('category'))
    if not faq:
        return api_response(404, "FAQ not found")
    return api_response(200, "FAQ updated successfully", faq_schema.dump(faq))

@faq_bp.route('/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    result = FAQService.delete_faq(faq_id)
    if not result:
        return api_response(404, "FAQ not found")
    return api_response(204, "FAQ deleted")
