from flask import Flask, Blueprint
from app.utils.error_handlers import register_error_handlers
import pytest

@pytest.fixture
def app_for_errors():
    app = Flask(__name__)
    register_error_handlers(app)

    @app.route('/test-400')
    def test_400():
        from werkzeug.exceptions import BadRequest
        raise BadRequest()

    @app.route('/test-401')
    def test_401():
        from werkzeug.exceptions import Unauthorized
        raise Unauthorized()

    @app.route('/test-403')
    def test_403():
        from werkzeug.exceptions import Forbidden
        raise Forbidden()

    @app.route('/test-404')
    def test_404():
        from werkzeug.exceptions import NotFound
        raise NotFound()

    @app.route('/test-500')
    def test_500():
        raise Exception("Internal server error")

    return app

@pytest.fixture
def client_for_errors(app_for_errors):
    return app_for_errors.test_client()

def test_bad_request(client_for_errors):
    response = client_for_errors.get('/test-400')
    assert response.status_code == 400
    assert response.json == {"message": "Bad request"}

def test_unauthorized(client_for_errors):
    response = client_for_errors.get('/test-401')
    assert response.status_code == 401
    assert response.json == {"message": "Unauthorized"}

def test_forbidden(client_for_errors):
    response = client_for_errors.get('/test-403')
    assert response.status_code == 403
    assert response.json == {"message": "Forbidden"}

def test_not_found(client_for_errors):
    response = client_for_errors.get('/test-404')
    assert response.status_code == 404
    assert response.json == {"message": "Not found"}

def test_internal_server_error(client_for_errors):
    response = client_for_errors.get('/test-500')
    assert response.status_code == 500
    assert response.json == {"message": "Internal server error"}
