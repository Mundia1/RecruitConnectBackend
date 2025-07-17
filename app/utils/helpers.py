
from flask import jsonify

def api_response(status_code, message, data=None):
    response = {
        "message": message,
        "data": data
    }
    if status_code == 204:
        return '', 204
    return jsonify(response), status_code
