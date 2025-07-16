import json


def test_create_job(client, employer):
    response = client.post('/jobs', json={
        "title": "Software Engineer",
        "description": "Work on amazing projects.",
        "location": "Remote",
        "employer_id": employer.id
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Software Engineer"


def test_get_jobs(client):
    response = client.get('/jobs')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_get_single_job(client, job_posting):
    response = client.get(f'/jobs/{job_posting.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == job_posting.id


def test_update_job(client, job_posting):
    response = client.patch(f'/jobs/{job_posting.id}', json={
        "title": "Updated Title"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Updated Title"


def test_delete_job(client, job_posting):
    response = client.delete(f'/jobs/{job_posting.id}')
    assert response.status_code == 204
