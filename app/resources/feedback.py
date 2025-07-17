from flask import Blueprint, request
from app.schemas.feedback import FeedbackSchema
from app.services.feedback_service import FeedbackService
from app.utils.helpers import api_response

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')
feedback_schema = FeedbackSchema()
feedbacks_schema = FeedbackSchema(many=True)

@feedback_bp.route('/', methods=['POST'])
def create_feedback():
    data = request.get_json()
    errors = feedback_schema.validate(data)
    if errors:
        return api_response(400, "Invalid data", errors)
    feedback = FeedbackService.create_feedback(data['user_id'], data['job_application_id'], data['rating'], data.get('comment'))
    return api_response(201, "Feedback created successfully", feedback_schema.dump(feedback))

@feedback_bp.route('/<int:feedback_id>', methods=['GET'])
def get_feedback(feedback_id):
    feedback = FeedbackService.get_feedback_by_id(feedback_id)
    if not feedback:
        return api_response(404, "Feedback not found")
    return api_response(200, "Feedback found", feedback_schema.dump(feedback))

@feedback_bp.route('/application/<int:job_application_id>', methods=['GET'])
def get_feedback_for_application(job_application_id):
    feedbacks = FeedbackService.get_feedback_for_application(job_application_id)
    return api_response(200, "Feedbacks retrieved", feedbacks_schema.dump(feedbacks))

@feedback_bp.route('/<int:feedback_id>', methods=['PATCH'])
def update_feedback(feedback_id):
    data = request.get_json()
    errors = feedback_schema.validate(data, partial=True)
    if errors:
        return api_response(400, "Invalid data", errors)
    feedback = FeedbackService.update_feedback(feedback_id, data.get('rating'), data.get('comment'))
    if not feedback:
        return api_response(404, "Feedback not found")
    return api_response(200, "Feedback updated successfully", feedback_schema.dump(feedback))

@feedback_bp.route('/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    result = FeedbackService.delete_feedback(feedback_id)
    if not result:
        return api_response(404, "Feedback not found")
    return api_response(204, "Feedback deleted")
