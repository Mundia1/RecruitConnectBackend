from flask import jsonify

def api_response(status, message, data=None):
    response = {"message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status