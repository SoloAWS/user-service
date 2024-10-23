import pytest
from fastapi.testclient import TestClient
from uuid import uuid4, UUID
import jwt
import os
from datetime import date

from app.models.model import User, Company, company_user_association, Manager
from app.schemas.user import UserDocumentInfo

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'secret_key')
ALGORITHM = "HS256"

def create_token(user_id: UUID, user_type: str):
    token_data = {
        "sub": str(user_id),
        "user_type": user_type
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

def create_user(db_session, **kwargs):
    user = User(
        first_name=kwargs.get('first_name', 'John'),
        last_name=kwargs.get('last_name', 'Doe'),
        document_type=kwargs.get('document_type', 'passport'),
        document_id=kwargs.get('document_id', 'AB123456')
    )
    db_session.add(user)
    db_session.commit()
    return user

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

def associate_user_company(db_session, user_id, company_id, document_type, document_id):
    db_session.execute(company_user_association.insert().values(
        company_id=company_id,
        user_id=user_id,
        document_type=document_type,
        document_id=document_id
    ))
    db_session.commit()

def test_create_user(client, db_session):
    company = create_company(db_session)
    user = create_user(db_session, first_name="John", last_name="Doe", document_type="passport", document_id="AB123456")
    
    associate_user_company(db_session, user.id, company.id, user.document_type, user.document_id)

    user_data = {
        "username": "user@example.com",
        "password": "testpassword",
        "first_name": "John",
        "last_name": "Doe",
        "birth_date": "1990-01-01",
        "phone_number": "9876543210",
        "country": "TestCountry",
        "city": "TestCity",
        "document_type": "passport",
        "document_id": "AB123456",
        "importance": 5,
        "allow_call": True,
        "allow_sms": True,
        "allow_email": True
    }

    response = client.post("/user/user/", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["first_name"] == user_data["first_name"]
    assert "id" in data

def test_create_user_duplicate_email(client, db_session):
    company = create_company(db_session, username="company2@example.com")
    user = create_user(db_session, first_name="John", last_name="Doe", document_type="passport", document_id="CD789012")
    
    associate_user_company(db_session, user.id, company.id, user.document_type, user.document_id)
    
    user_data = {
        "username": "duplicate@example.com",
        "password": "testpassword",
        "first_name": "John",
        "last_name": "Doe",
        "birth_date": "1990-01-01",
        "phone_number": "9876543210",
        "country": "TestCountry",
        "city": "TestCity",
        "document_type": "passport",
        "document_id": "CD789012",
        "importance": 5,
        "allow_call": True,
        "allow_sms": True,
        "allow_email": True
    }
    
    client.post("/user/user/", json=user_data)
    response = client.post("/user/user/", json=user_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

# def test_view_user_unauthorized(client, db_session):
#     user_id = uuid4()
#     response = client.get(f"/user/user/{user_id}")
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Authentication required"

def test_get_user_companies(client, db_session):
    company_1 = create_company(db_session, username="company1@example.com", name="Company One")
    company_2 = create_company(db_session, username="company2@example.com", name="Company Two")
    user = create_user(db_session, first_name="Multi", last_name="User", document_type="passport", document_id="IJ567890")

    associate_user_company(db_session, user.id, company_1.id, user.document_type, user.document_id)
    associate_user_company(db_session, user.id, company_2.id, user.document_type, user.document_id)

    user_data = {
        "username": "multicompanyuser@example.com",
        "password": "testpassword",
        "first_name": "Multi",
        "last_name": "User",
        "birth_date": "1990-01-01",
        "phone_number": "5556667777",
        "country": "TestCountry",
        "city": "TestCity",
        "document_type": "passport",
        "document_id": "IJ567890",
        "importance": 5,
        "allow_call": True,
        "allow_sms": True,
        "allow_email": True
    }
    client.post("/user/user/", json=user_data)

    user_doc_info = UserDocumentInfo(document_type=user.document_type, document_id=user.document_id)
    
    token = create_token(user.id, "user")

    response = client.post("/user/user/companies", json=user_doc_info.dict(), headers={"token": token})
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert "companies" in data
    assert len(data["companies"]) == 2

def test_get_user_companies_no_companies(client, db_session):
    user = create_user(db_session)
    token = create_token(user.id, "user")
    user_doc_info = UserDocumentInfo(document_type=user.document_type, document_id=user.document_id)
    
    response = client.post("/user/user/companies", json=user_doc_info.dict(), headers={"token": token})
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(user.id)
    assert len(data["companies"]) == 0

def test_get_user_companies_user_not_found(client, db_session):
    user = create_user(db_session)
    token = create_token(user.id, "user")
    user_doc_info = UserDocumentInfo(document_type="passport", document_id="NONEXISTENT")
    
    response = client.post("/user/user/companies", json=user_doc_info.dict(), headers={"token": token})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# def test_get_user_companies_unauthorized(client, db_session):
#     user = create_user(db_session)
#     user_doc_info = UserDocumentInfo(document_type=user.document_type, document_id=user.document_id)
    
#     response = client.post("/user/user/companies", json=user_doc_info.dict())
#     assert response.status_code == 401
#     assert response.json()["detail"] == "Authentication required"

# def test_get_user_companies_wrong_user(client, db_session):
#     user1 = create_user(db_session, first_name="User", last_name="One", document_type="passport", document_id="KL123456")
#     user2 = create_user(db_session, first_name="User", last_name="Two", document_type="passport", document_id="MN789012")
    
#     token = create_token(user2.id, "user")
#     user_doc_info = UserDocumentInfo(document_type=user1.document_type, document_id=user1.document_id)
    
#     response = client.post("/user/user/companies", json=user_doc_info.dict(), headers={"token": token})
#     assert response.status_code == 403
#     assert response.json()["detail"] == "Not authorized to view this user's companies"

# def test_get_user_companies_company_user(client, db_session):
#     user = create_user(db_session)
#     company = create_company(db_session)
    
#     token = create_token(company.id, "company")
#     user_doc_info = UserDocumentInfo(document_type=user.document_type, document_id=user.document_id)
    
#     response = client.post("/user/user/companies", json=user_doc_info.dict(), headers={"token": token})
#     assert response.status_code == 403
#     assert response.json()["detail"] == "Not authorized to view user companies"