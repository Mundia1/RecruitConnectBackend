from app.models.faq import FAQ
from app.extensions import db

class FAQService:
    @staticmethod
    def create_faq(question, answer, category=None):
        faq = FAQ(question=question, answer=answer, category=category)
        db.session.add(faq)
        db.session.commit()
        return faq

    @staticmethod
    def get_faq_by_id(faq_id):
        return db.session.get(FAQ, faq_id)

    @staticmethod
    def get_all_faqs():
        return FAQ.query.all()

    @staticmethod
    def update_faq(faq_id, question=None, answer=None, category=None):
        faq = db.session.get(FAQ, faq_id)
        if faq:
            if question is not None:
                faq.question = question
            if answer is not None:
                faq.answer = answer
            if category is not None:
                faq.category = category
            db.session.commit()
        return faq

    @staticmethod
    def delete_faq(faq_id):
        faq = db.session.get(FAQ, faq_id)
        if faq:
            db.session.delete(faq)
            db.session.commit()
            return True
        return False
