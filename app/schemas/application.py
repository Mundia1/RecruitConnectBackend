from marshmallow import Schema, fields, validate

class ApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    applied_at = fields.DateTime(dump_only=True)
    status = fields.Str(validate=validate.OneOf(['submitted', 'viewed', 'rejected', 'accepted']), 
                       missing='submitted')
    user_id = fields.Int(required=True)
    job_posting_id = fields.Int(required=True)
    resume_url = fields.Str(required=False)  # Will be updated after Google Form submission
