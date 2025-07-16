from marshmallow import Schema, fields, validate


class JobPostingSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=3))
    description = fields.Str(required=True, validate=validate.Length(min=10))
    location = fields.Str(required=True)
    employer_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
