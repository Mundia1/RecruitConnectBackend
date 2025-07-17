from marshmallow import Schema, fields, validate

class FeedbackSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    job_application_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)
