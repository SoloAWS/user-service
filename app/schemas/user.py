from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import date
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re

class AbcallUserCreate(BaseModel):
    username: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+$')
    last_name: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+$')
    
        
    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]{1,50}$', v):
            raise ValueError('Name must contain only letters and be max 50 characters')
        return v

class CompanyCreate(AbcallUserCreate):
    name: str
    birth_date: date
    phone_number: str
    country: str
    city: str

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError('Birth date cannot be in the future')
        return v

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    first_name: str
    last_name: str
    birth_date: date
    phone_number: str
    username: EmailStr
    country: str
    city: str
    registration_date: datetime

    model_config = {
        "from_attributes": True
    }

class CompanyIdsRequest(BaseModel):
    company_ids: List[UUID]
    
class CompanyPlanRequest(BaseModel):
    company_id: UUID
    plan_id: UUID

class UserCreate(AbcallUserCreate):    
    document_id: str
    document_type: str
    birth_date: date
    phone_number: str
    importance: int = Field(..., ge=1, le=10)
    allow_call: bool
    allow_sms: bool
    allow_email: bool

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]{1,50}$', v):
            raise ValueError('Name must contain only letters and be max 50 characters')
        return v

    @field_validator('importance')
    @classmethod
    def validate_importancia(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError('Importance must be between 1 and 10')
        return v

    model_config = {
        "from_attributes": True
    }

class UserResponse(BaseModel):
    id: UUID
    username: EmailStr
    first_name: str
    last_name: str
    document_id: str
    document_type: str
    birth_date: date
    phone_number: str
    importance: int
    allow_call: bool
    allow_sms: bool
    allow_email: bool
    registration_date: datetime

    model_config = {
        "from_attributes": True
    }
    
class ManagerResponse(BaseModel):
    id: UUID
    username: EmailStr
    first_name: str
    last_name: str
    registration_date: datetime

    class Config:
        from_attributes = True
        
class UserDocumentInfo(BaseModel):
    document_type: str
    document_id: str

class UserCompaniesResponse(BaseModel):
    user_id: UUID
    companies: List[CompanyResponse]
    
class UserIdRequest(BaseModel):
    id: UUID