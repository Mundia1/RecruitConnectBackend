
from flask import jsonify

def api_response(status_code, message, data=None):
    response = {
        "message": message,
        "data": data
    }
    if data is None:
        del response["data"]
    return jsonify(response), status_code
