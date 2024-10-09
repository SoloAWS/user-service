import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
import uuid

from app.main import app
from app.session import get_db
from app.models.model import Base, Company
from app.schemas.user import CompanyCreate, CompanyResponse


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

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
    TestingSessionLocal().close()
    engine.dispose()
    
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
    response = client.post("/company/", json=company_data)
    assert response.status_code == 201

    
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

    response = client.get(f"/company/{company['id']}")
    assert response.status_code == 200
    data = response.json()

    assert data["username"] == company['username']
    assert data["id"] == str(company['id'])

def test_view_nonexistent_company():
    non_existent_id = uuid.uuid4()
    response = client.get(f"/company/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found"