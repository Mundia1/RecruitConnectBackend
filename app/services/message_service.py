from app.models.message import Message
from app.extensions import db

class MessageService:
    @staticmethod
    def create_message(sender_id, receiver_id, content):
        message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
        db.session.add(message)
        db.session.commit()
        return message

    @staticmethod
    def get_message_by_id(message_id):
        return db.session.get(Message, message_id)

    @staticmethod
    def get_messages_between_users(user1_id, user2_id):
        return Message.query.filter(
            ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
        ).order_by(Message.sent_at).all()

    @staticmethod
    def mark_message_as_read(message_id):
        message = db.session.get(Message, message_id)
        if message:
            message.is_read = True
            db.session.commit()
        return message

    @staticmethod
    def delete_message(message_id):
        message = db.session.get(Message, message_id)
        if message:
            db.session.delete(message)
            db.session.commit()
            return True
        return False
