import pytest
from app.services.job_service import JobService

def test_job_service_exists():
    
    assert JobService is not None

def test_job_service_list_jobs_stub():
    
    with pytest.raises(AttributeError):
        JobService.list_jobs()