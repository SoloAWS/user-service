import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.model import Manager, ABCallUser
from app.schemas.user import AbcallUserCreate
from app.session import get_db
from uuid import uuid4
import jwt
import os

client = TestClient(app)

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'secret_key')
ALGORITHM = "HS256"

def create_token(user_id: str, user_type: str):
    token_data = {
        "sub": user_id,
        "user_type": user_type
    }
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

def test_create_manager(db_session: Session):
    manager_data = {
        "username": "manager@example.com",
        "password": "testpassword",
        "first_name": "Manager",
        "last_name": "User",
        "birth_date": "1990-01-01",
        "phone_number": "1234567890",
        "country": "TestCountry",
        "city": "TestCity",
        "document_type": "passport",
        "document_id": "AB123456",
        "importance": 5,
        "allow_call": True,
        "allow_sms": True,
        "allow_email": True
    }

    response = client.post("/user/manager/", json=manager_data)
    print(response.json())
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == manager_data["username"]
    assert data["first_name"] == manager_data["first_name"]
    assert "id" in data

def test_create_manager_duplicate_username(db_session: Session):
    manager_data = {
        "username": "duplicate@example.com",
        "password": "testpassword",
        "first_name": "Manager",
        "last_name": "User",
        "birth_date": "1990-01-01",
        "phone_number": "1234567890",
        "country": "TestCountry",
        "city": "TestCity",
        "document_type": "passport",
        "document_id": "AB123456",
        "importance": 5,
        "allow_call": True,
        "allow_sms": True,
        "allow_email": True
    }

    client.post("/user/manager/", json=manager_data)
    response = client.post("/user/manager/", json=manager_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_get_manager_not_found(db_session: Session):
    token = create_token(str(uuid4()), "manager")
    response = client.get(f"/user/manager/{uuid4()}", headers={"authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Manager not found"

def test_get_manager_unauthorized(db_session: Session):
    manager = Manager(
        username="manager3@example.com",
        password="hashed_password",
        first_name="Manager",
        last_name="User"
    )
    db_session.add(manager)
    db_session.commit()

    token = create_token(str(manager.id), "user")
    response = client.get(f"/user/manager/{manager.id}", headers={"authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to view manager details"