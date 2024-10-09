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

class CompanyCreate(AbcallUserCreate):
    name: str
    birth_date: date
    phone_number: str
    country: str
    city: str

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]{1,50}$', v):
            raise ValueError('Name must contain only letters and be max 50 characters')
        return v

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