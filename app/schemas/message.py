from marshmallow import Schema, fields

class MessageSchema(Schema):
    id = fields.Int(dump_only=True)
    sender_id = fields.Int(required=True)
    receiver_id = fields.Int(required=True)
    content = fields.Str(required=True)
    sent_at = fields.DateTime(dump_only=True)
    is_read = fields.Bool(dump_only=True)
