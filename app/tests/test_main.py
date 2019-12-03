import time
from typing import Dict

from starlette.testclient import TestClient

from ..main import app, JOB_FINAL_STATES, JobStatus

client = TestClient(app)


MAX_RESPONSE_WAIT = 2  # sec


def _poll_vehicle_size(json):
    """Helper for dispatching job to calculate vehicle size and polling for its
    response.
    """
    response = client.post("/vehicle_size", json=json)
    response_json = response.json()
    assert len(response_json.keys()) == 1
    assert "job_id" in response_json

    job_response = None
    awaiting_response = True
    total_wait = 0
    while awaiting_response and total_wait <= MAX_RESPONSE_WAIT:
        job_response = _job(response_json['job_id'])
        if job_response.status_code != 200:
            raise Exception("Job response failed")
        if job_response.json()['job_status'] in JOB_FINAL_STATES:
            awaiting_response = False
        time.sleep(0.1)
        total_wait += 0.1

    return job_response


def _job(job_id):
    """Helper to call job_id endpoint"""
    response = client.get(f"/job/{job_id}")
    response_json = response.json()
    assert len(response_json.keys()) == 3
    assert "job_id" in response_json.keys()
    assert "job_status" in response_json.keys()
    assert "job_result" in response_json.keys()
    return response


def _assert_vehicle_size_response(
    json: Dict,
    expected_status_code: int,
    expected_job_status: JobStatus,
    expected_size: str,
):
    """Helper to assert result from job when requesting vehicle_size"""
    job_response = _poll_vehicle_size(json=json)
    job_response_json = job_response.json()
    assert job_response.status_code == expected_status_code
    assert job_response_json['job_status'] == expected_job_status
    assert job_response_json['job_result'] == {"vehicle_size": expected_size}


################################
# /vehicle_size and /job tests #
################################

def test_very_small_package():
    request = [{"length": 1, "width": 1, "height": 1, "weight": 5,
                "quantity": 1}]
    _assert_vehicle_size_response(request, 200, JobStatus.COMPLETE, "compact")


def test_weight():
    request = [{"length": 20, "width": 20, "height": 30, "weight": 60,
                "quantity": 1}]
    _assert_vehicle_size_response(request, 200, JobStatus.COMPLETE, "van")


def test_weight_and_height():
    request = [{"length": 90, "width": 50, "height": 62, "weight": 60,
                "quantity": 1}]
    _assert_vehicle_size_response(request, 200, JobStatus.COMPLETE, "truck")


def test_weight_and_orientation():
    request = [{"length": 60, "width": 90, "height": 50, "weight": 60,
                "quantity": 1}]
    _assert_vehicle_size_response(request, 200, JobStatus.COMPLETE, "van")


def test_very_large_package():
    request = [{"length": 100, "width": 100, "height": 100, "weight": 1,
                "quantity": 1}]
    _assert_vehicle_size_response(request, 200, JobStatus.COMPLETE, None)


def test_very_heavy_package():
    request = [{"length": 1, "width": 1, "height": 1, "weight": 1000,
                "quantity": 1}]
    _assert_vehicle_size_response(request, 200, JobStatus.COMPLETE, None)


def test_many_small_packages():
    request = [{"length": 2, "width": 2, "height": 1, "weight": 0.001,
                "quantity": 12121}]  # perfect fit for sedan
    _assert_vehicle_size_response(request, 200, JobStatus.COMPLETE, "sedan")
