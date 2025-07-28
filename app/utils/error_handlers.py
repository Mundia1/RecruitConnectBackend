
from flask import jsonify
import structlog
from marshmallow import ValidationError

log = structlog.get_logger()

def handle_marshmallow_validation_error(e):
    if isinstance(e, ValidationError):
        log.error("Marshmallow validation error", errors=e.messages, exc_info=True)
        return jsonify(message="Validation error", errors=e.messages), 400
    else:
        log.error("An unexpected error occurred", exc_info=True)
        return jsonify(message="An unexpected error occurred"), 500

def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        log.error("Bad request", error=error)
        return jsonify(message="Bad request"), 400

    @app.errorhandler(401)
    def unauthorized(error):
        log.error("Unauthorized", error=error)
        return jsonify(message="Unauthorized"), 401

    @app.errorhandler(403)
    def forbidden(error):
        log.error("Forbidden", error=error)
        return jsonify(message="Forbidden"), 403

    @app.errorhandler(404)
    def not_found(error):
        log.error("Not found", error=error)
        return jsonify(message="Not found"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        log.error("Internal server error", error=error)
        return jsonify(message="Internal server error"), 500
