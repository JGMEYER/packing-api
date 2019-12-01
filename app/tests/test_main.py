from starlette.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_vehicle_size_simple():
    """Test responses for single packages."""

    # Test very small package
    response = client.post(
        "/vehicle_size",
        json=[{"length": 1, "width": 1, "height": 1, "weight": 5,
               "quantity": 1}],
    )
    assert response.status_code == 200
    assert response.json() == {"vehicle_size": "compact"}

    # Test weight
    response = client.post(
        "/vehicle_size",
        json=[{"length": 20, "width": 20, "height": 30, "weight": 60,
               "quantity": 1}],
    )
    assert response.status_code == 200
    assert response.json() == {"vehicle_size": "van"}

    # Test weight and height
    response = client.post(
        "/vehicle_size",
        json=[{"length": 90, "width": 50, "height": 62, "weight": 60,
               "quantity": 1}],
    )
    assert response.status_code == 200
    assert response.json() == {"vehicle_size": "truck"}

    # Test weight and orientation
    response = client.post(
        "/vehicle_size",
        json=[{"length": 60, "width": 90, "height": 50, "weight": 60,
               "quantity": 1}],
    )
    assert response.status_code == 200
    assert response.json() == {"vehicle_size": "van"}
