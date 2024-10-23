import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
import jwt
import os

from app.models.model import Company

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'secret_key')
ALGORITHM = "HS256"

def test_create_company(client, db_session):
    company_data = {
        "username": "test@example.com",
        "password": "testpassword",
        "first_name": "John",
        "last_name": "Doe",
        "name": "Test Company",
        "birth_date": "1990-01-01",
        "phone_number": "1234567890",
        "country": "TestCountry",
        "city": "TestCity"
    }

    response = client.post("/user/company/", json=company_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == company_data["username"]
    assert data["name"] == company_data["name"]
    assert "id" in data

def test_create_company_duplicate_email(client, db_session):
    company_data = {
        "username": "duplicate@example.com",
        "password": "testpassword",
        "first_name": "John",
        "last_name": "Doe",
        "name": "Test Company",
        "birth_date": "1990-01-01",
        "phone_number": "1234567890",
        "country": "TestCountry",
        "city": "TestCity"
    }

    client.post("/user/company/", json=company_data)
    response = client.post("/user/company/", json=company_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_view_company(client, db_session):
    # Create a test company
    company_data = {
        "username": "view@example.com",
        "password": "testpassword",
        "first_name": "Jane",
        "last_name": "Doe",
        "name": "View Company",
        "birth_date": "1990-01-01",
        "phone_number": "1234567890",
        "country": "TestCountry",
        "city": "TestCity"
    }
    response = client.post("/user/company/", json=company_data)
    company_id = response.json()["id"]

    # Create a JWT token for authentication
    token_data = {
        "sub": company_id,
        "user_type": "company"
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    # Test viewing the company
    response = client.get(f"/user/company/{company_id}", headers={"token": token})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == company_data["username"]
    assert data["name"] == company_data["name"]

# def test_view_company_unauthorized(client, db_session):
#     company_id = str(uuid4())
#     response = client.get(f"/user/company/{company_id}")
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Authentication required"

# def test_view_company_wrong_user(client, db_session):
#     # Create a test company
#     company_data = {
#         "username": "wrong@example.com",
#         "password": "testpassword",
#         "first_name": "Wrong",
#         "last_name": "User",
#         "name": "Wrong Company",
#         "birth_date": "1990-01-01",
#         "phone_number": "1234567890",
#         "country": "TestCountry",
#         "city": "TestCity"
#     }
#     response = client.post("/user/company/", json=company_data)
#     company_id = response.json()["id"]

#     # Create a JWT token for a different company
#     token_data = {
#         "sub": str(uuid4()),
#         "user_type": "company"
#     }
#     token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

#     # Test viewing the company with wrong user
#     response = client.get(f"/user/company/{company_id}", headers={"token": token})
#     assert response.status_code == 403
#     assert response.json()["detail"] == "Not authorized to view this company"

def test_view_nonexistent_company(client, db_session):
    nonexistent_id = str(uuid4())
    token_data = {
        "sub": nonexistent_id,
        "user_type": "company"
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(f"/user/company/{nonexistent_id}", headers={"token": token})
    assert response.status_code == 404
    assert response.json()["detail"] == "Company not found"
    
def test_assign_plan_success(client):
    company_data = {
        "username": "view@example.com",
        "password": "testpassword",
        "first_name": "Jane",
        "last_name": "Doe",
        "name": "View Company",
        "birth_date": "1990-01-01",
        "phone_number": "1234567890",
        "country": "TestCountry",
        "city": "TestCity"
    }
    response = client.post("/user/company/", json=company_data)
    company_id = response.json()["id"]
    
    #Create a JWT token for a different company
    token_data = {
        "sub": str(company_id),
        "user_type": "company"
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    response = client.post("/user/company/assign-plan", json={"company_id": company_id, "plan_id": str(uuid4())}, headers={"token": token})
    assert response.status_code == 200
    assert response.json() == {"message": "Plan assigned successfully"}

def test_assign_plan_invalid_user(client):
    company_data = {
        "username": "view@example.com",
        "password": "testpassword",
        "first_name": "Jane",
        "last_name": "Doe",
        "name": "View Company",
        "birth_date": "1990-01-01",
        "phone_number": "1234567890",
        "country": "TestCountry",
        "city": "TestCity"
    }
    response = client.post("/user/company/", json=company_data)
    company_id = response.json()["id"]
    
    #Create a JWT token for a different company
    token_data = {
        "sub": str(company_id),
        "user_type": "company"
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    response = client.post("/user/company/assign-plan", json={"company_id": str(uuid4()), "plan_id": str(uuid4())}, headers={"token": token})
    
    assert response.json()["detail"] == "User not found"
    assert response.status_code == 404