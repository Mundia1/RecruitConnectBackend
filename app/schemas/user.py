import html
from marshmallow import Schema, fields, validate, pre_load
from marshmallow.fields import Email

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    role = fields.Str(validate=validate.OneOf(['job_seeker', 'employer', 'admin']))
    first_name = fields.Str()
    last_name = fields.Str()
    profile_picture = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class UserRegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)

    @pre_load
    def sanitize_input(self, data, **kwargs):
        if 'first_name' in data:
            data['first_name'] = html.escape(data['first_name'])
        if 'last_name' in data:
            data['last_name'] = html.escape(data['last_name'])
        return data

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
