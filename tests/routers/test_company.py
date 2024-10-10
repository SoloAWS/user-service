import os
import uuid
import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.session import get_db
from app.models.model import Base
from app.session import SessionConfig

# Modify the SessionConfig class to support an alternate URL
class TestSessionConfig(SessionConfig):
    def url(self):
        return os.environ["SQLALCHEMY_DATABASE_URL"]

# Create the engine and session for testing
session_config = TestSessionConfig()
engine = create_engine(session_config.url(), connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")

def test_create_company():
    company_data = {
        "username": "testcompany@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "Company",
        "name": "Test Company Inc.",
        "greeting": "Welcome to Test Company",
        "farewell": "Thank you for choosing Test Company",
        "birth_date": "2000-01-01",
        "phone_number": "1234567890",
        "country": "Test Country",
        "city": "Test City"
    }
    response = client.post("/company/", json=company_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == company_data["username"]
    assert "id" in data

def test_create_company_duplicate_email():
    company_data = {
        "username": "duplicate@example.com",
        "password": "testpassword",
        "first_name": "Duplicate",
        "last_name": "Company",
        "name": "Duplicate Company Inc.",
        "greeting": "Welcome to Duplicate Company",
        "farewell": "Thank you for choosing Duplicate Company",
        "birth_date": "2000-01-01",
        "phone_number": "1234567890",
        "country": "Test Country",
        "city": "Test City"
    }
    # Create the first company
    response = client.post("/company/", json=company_data)
    assert response.status_code == 201

    # Attempt to create the duplicate company
    response = client.post("/company/", json=company_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_view_company():
    company_data = {
        "username": "testcompany2@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "Company",
        "name": "Test Company Inc.",
        "greeting": "Welcome to Test Company",
        "farewell": "Thank you for choosing Test Company",
        "birth_date": "2000-01-01",
        "phone_number": "1234567890",
        "country": "Test Country",
        "city": "Test City"
    }
    response = client.post("/company/", json=company_data)
    assert response.status_code == 201
    company = response.json()

    token = create_jwt_token(user_type="company", sub=company['id'])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/company/{company['id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["username"] == company['username']
    assert data["id"] == str(company['id'])

def test_view_nonexistent_company():
    non_existent_id = uuid.uuid4()
    token = create_jwt_token(user_type="manager", sub=non_existent_id)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/company/{non_existent_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found"

def test_view_company_unauthorized():
    company_data = {
        "username": "testcompany3@example.com",
        "password": "testpassword",
        "first_name": "Test",
        "last_name": "Company",
        "name": "Test Company Inc.",
        "greeting": "Welcome to Test Company",
        "farewell": "Thank you for choosing Test Company",
        "birth_date": "2000-01-01",
        "phone_number": "1234567890",
        "country": "Test Country",
        "city": "Test City"
    }
    response = client.post("/company/", json=company_data)
    assert response.status_code == 201
    company = response.json()

    # Test without token
    response = client.get(f"/company/{company['id']}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"

    # Test with a token of a different user type
    token = create_jwt_token(user_type="employee", sub=company['id'])
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/company/{company['id']}", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to view companies"
