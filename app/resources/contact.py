from flask import Blueprint
from flask_restful import Api, Resource
from app.schemas.contact import ContactSchema
from app.services.contact_service import ContactService
from app.utils.error_handlers import handle_marshmallow_validation_error

contact_bp = Blueprint('contact', __name__)
api = Api(contact_bp)

class ContactResource(Resource):
    def post(self):
        try:
            data = ContactSchema().load(self.api.payload)
            result = ContactService.send_contact_message(data)
            return result, 200
        except Exception as e:
            return handle_marshmallow_validation_error(e)

api.add_resource(ContactResource, '/contact')
