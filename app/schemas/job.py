from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime

class JobSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(required=True)
    company = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    location = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    salary = fields.Int(allow_none=True)
    job_type = fields.Str(validate=validate.OneOf(['Full-time', 'Part-time', 'Contract', 'Temporary', 'Internship', 'Volunteer']))
    requirements = fields.Str()
    deadline = fields.DateTime(format='iso')
    posted_at = fields.DateTime(dump_only=True)
    admin_id = fields.Int(required=True)

    @validates('deadline')
    def validate_deadline(self, value):
        if value and value < datetime.utcnow():
            raise ValidationError('Deadline must be in the future')