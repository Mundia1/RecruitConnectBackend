import pytest
import json
from unittest.mock import patch, MagicMock
from app import create_app
from app.extensions import cache

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def mock_job_service():
    with patch('app.resources.job.JobService') as mock_service:
        yield mock_service

@pytest.fixture(autouse=True)
def mock_cache():
    with patch('app.resources.job.cache') as mock_cache_obj:
        mock_cache_obj.cached.side_effect = lambda timeout: lambda f: f
        yield mock_cache_obj

def test_create_job_posting_success(client, mock_job_service, mock_cache):
    mock_job_service.create_job.return_value = {
        "id": 1,
        "title": "Software Engineer",
        "description": "Develop software",
        "requirements": "Python",
        "location": "Remote",
        "admin_id": 1
    }
    
    job_data = {
        "title": "Software Engineer",
        "description": "Develop software",
        "requirements": "Python",
        "location": "Remote",
        "admin_id": 1
    }
    
    response = client.post('/api/v1/jobs/', data=json.dumps(job_data), content_type='application/json')
    
    assert response.status_code == 201
    assert response.json['message'] == "Job created successfully"
    assert response.json['data']['title'] == "Software Engineer"
    mock_job_service.create_job.assert_called_once()
    mock_cache.clear.assert_called_once()

def test_create_job_posting_invalid_data(client, mock_job_service):
    job_data = {
        "title": "Software Engineer",
        "description": "Develop software",
        "requirements": "Python",
        "location": "Remote",
        # Missing admin_id
    }
    
    response = client.post('/api/v1/jobs/', data=json.dumps(job_data), content_type='application/json')
    
    assert response.status_code == 400
    assert response.json['message'] == "Invalid data"
    assert "admin_id" in response.json['data']
    mock_job_service.create_job.assert_not_called()

def test_create_job_posting_exception(client, mock_job_service):
    mock_job_service.create_job.side_effect = Exception("Database connection error")
    job_data = {
        "title": "Software Engineer",
        "description": "Develop software",
        "requirements": "Python",
        "location": "Remote",
        "admin_id": 1
    }
    response = client.post('/api/v1/jobs/', data=json.dumps(job_data), content_type='application/json')
    assert response.status_code == 500
    assert response.json['message'] == "Error creating job"
    assert response.json['data'] == "Database connection error"

def test_get_jobs_success(client, mock_job_service):
    mock_job_service.get_all_jobs.return_value = [
        {"id": 1, "title": "Job 1", "description": "Desc 1", "requirements": "Req 1", "location": "Loc 1", "admin_id": 1},
        {"id": 2, "title": "Job 2", "description": "Desc 2", "requirements": "Req 2", "location": "Loc 2", "admin_id": 2}
    ]
    
    response = client.get('/api/v1/jobs/')
    
    assert response.status_code == 200
    assert response.json['message'] == "Jobs retrieved"
    assert len(response.json['data']) == 2
    assert response.json['data'][0]['title'] == "Job 1"
    mock_job_service.get_all_jobs.assert_called_once()

def test_get_job_success(client, mock_job_service):
    mock_job_service.get_job_by_id.return_value = {
        "id": 1,
        "title": "Software Engineer",
        "description": "Develop software",
        "requirements": "Python",
        "location": "Remote",
        "admin_id": 1
    }
    
    response = client.get('/api/v1/jobs/1')
    
    assert response.status_code == 200
    assert response.json['message'] == "Job found"
    assert response.json['data']['title'] == "Software Engineer"
    mock_job_service.get_job_by_id.assert_called_once_with(1)

def test_get_job_not_found(client, mock_job_service):
    mock_job_service.get_job_by_id.return_value = None
    
    response = client.get('/api/v1/jobs/999')
    
    assert response.status_code == 404
    assert response.json['message'] == "Job not found"
    mock_job_service.get_job_by_id.assert_called_once_with(999)

def test_update_job_success(client, mock_job_service, mock_cache):
    mock_job_service.update_job.return_value = {
        "id": 1,
        "title": "Updated Title",
        "description": "Develop software",
        "requirements": "Python",
        "location": "Remote",
        "admin_id": 1
    }
    
    update_data = {"title": "Updated Title"}
    
    response = client.patch('/api/v1/jobs/1', data=json.dumps(update_data), content_type='application/json')
    
    assert response.status_code == 200
    assert response.json['message'] == "Job updated successfully"
    assert response.json['data']['title'] == "Updated Title"
    mock_job_service.update_job.assert_called_once_with(1, update_data)
    mock_cache.clear.assert_called_once()

def test_update_job_not_found(client, mock_job_service):
    mock_job_service.update_job.return_value = None
    
    update_data = {"title": "Updated Title"}
    
    response = client.patch('/api/v1/jobs/999', data=json.dumps(update_data), content_type='application/json')
    
    assert response.status_code == 404
    assert response.json['message'] == "Job not found"
    mock_job_service.update_job.assert_called_once_with(999, update_data)

def test_update_job_invalid_data(client, mock_job_service):
    update_data = {"title": "Updated Title", "admin_id": None} # Invalid admin_id
    
    response = client.patch('/api/v1/jobs/1', data=json.dumps(update_data), content_type='application/json')
    
    assert response.status_code == 400
    assert response.json['message'] == "Invalid data"
    assert "admin_id" in response.json['data']
    mock_job_service.update_job.assert_not_called()

def test_delete_job_success(client, mock_job_service):
    mock_job_service.delete_job.return_value = True
    
    response = client.delete('/api/v1/jobs/1')
    
    assert response.status_code == 204
    assert not response.data
    mock_job_service.delete_job.assert_called_once_with(1)

def test_delete_job_not_found(client, mock_job_service):
    mock_job_service.delete_job.return_value = False
    
    response = client.delete('/api/v1/jobs/999')
    
    assert response.status_code == 404
    assert response.json['message'] == "Job not found"
    mock_job_service.delete_job.assert_called_once_with(999)