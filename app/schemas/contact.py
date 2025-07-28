from marshmallow import Schema, fields, validate

class ContactSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(min=1, max=120))
    message = fields.String(required=True, validate=validate.Length(min=1, max=1000))
