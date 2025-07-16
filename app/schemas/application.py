from marshmallow import Schema, fields, validate

class JobApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    applied_at = fields.DateTime(dump_only=True)
    status = fields.Str(validate=validate.OneOf(['pending', 'reviewed', 'accepted', 'rejected']))
    job_seeker_id = fields.Int(required=True)
    job_posting_id = fields.Int(required=True)