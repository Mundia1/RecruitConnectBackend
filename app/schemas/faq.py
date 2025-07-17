from marshmallow import Schema, fields

class FAQSchema(Schema):
    id = fields.Int(dump_only=True)
    question = fields.Str(required=True)
    answer = fields.Str(required=True)
    category = fields.Str()
    created_at = fields.DateTime(dump_only=True)
