import pytest
from fastapi.testclient import TestClient
from uuid import uuid4, UUID
import jwt
import os
from datetime import date

from app.models.model import Company

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'secret_key')
ALGORITHM = "HS256"

def create_token(user_id: UUID, user_type: str):
    token_data = {
        "sub": str(user_id),
        "user_type": user_type
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

def create_company(db_session, **kwargs):
    company_id = kwargs.get('id', uuid4())
    company = Company(
        id=company_id,
        username=kwargs.get('username', 'company@example.com'),
        password="hashed_password",
        first_name=kwargs.get('first_name', 'Company'),
        last_name=kwargs.get('last_name', 'Owner'),
        name=kwargs.get('name', 'Test Company'),
        birth_date=kwargs.get('birth_date', date(1990, 1, 1)),
        phone_number=kwargs.get('phone_number', '1234567890'),
        country=kwargs.get('country', 'TestCountry'),
        city=kwargs.get('city', 'TestCity')
    )
    db_session.add(company)
    db_session.commit()
    return company

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

def test_view_company_unauthorized(client, db_session):
    company_id = str(uuid4())
    response = client.get(f"/user/company/{company_id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"

def test_view_company_wrong_user(client, db_session):
    # Create a test company
    company_data = {
        "username": "wrong@example.com",
        "password": "testpassword",
        "first_name": "Wrong",
        "last_name": "User",
        "name": "Wrong Company",
        "birth_date": "1990-01-01",
        "phone_number": "1234567890",
        "country": "TestCountry",
        "city": "TestCity"
    }
    response = client.post("/user/company/", json=company_data)
    company_id = response.json()["id"]

    # Create a JWT token for a different company
    token_data = {
        "sub": str(uuid4()),
        "user_type": "company"
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    # Test viewing the company with wrong user
    response = client.get(f"/user/company/{company_id}", headers={"token": token})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to view this company"

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
    
    assert response.json()["detail"] == "Company not found"
    assert response.status_code == 404
    

def test_get_companies_success(client, db_session):
    company1 = create_company(db_session, username="company1@example.com", name="Company One")
    company2 = create_company(db_session, username="company2@example.com", name="Company Two")
    
    response = client.post("/user/company/get-by-id", json={"company_ids": [str(company1.id), str(company2.id)]}, headers={"token": create_token(company1.id, "manager")})
    assert response.status_code == 200
    assert response.json() == [
        {"company_id": str(company1.id), "name": company1.name},
        {"company_id": str(company2.id), "name": company2.name}
    ]

def test_get_companies_invalid_ids(client):
    invalid_id1 = uuid4()
    invalid_id2 = uuid4()
    
    response = client.post("/user/company/get-by-id", json={"company_ids": [str(invalid_id1), str(invalid_id2)]}, headers={"token": create_token(uuid4(), "manager")})
    assert response.status_code == 404
    assert response.json()["detail"] == "No companies found"