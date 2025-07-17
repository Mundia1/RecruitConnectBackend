from marshmallow import Schema, fields, validate

class JobSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    location = fields.Str()
    requirements = fields.Str()
    deadline = fields.DateTime(format='iso')
    posted_at = fields.DateTime(dump_only=True)
    admin_id = fields.Int(required=True)