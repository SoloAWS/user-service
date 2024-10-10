from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_validation_error_handler():
    response = client.get("/company/invalid-uuid")
    assert response.status_code == 422
    assert response.json()["message"] == "Validation Error"
