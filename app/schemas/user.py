from pydantic import BaseModel, EmailStr, field_validator
from datetime import date
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re

class AbcallUserBase(BaseModel):
    id: str
    username: str
    password: str
    name: str
    email: EmailStr
    registration_date: datetime

class AbcallUserCreate(AbcallUserBase):
    pass

class AbcallUserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None

class AbcallUserResponse(AbcallUserBase):
    pass

class CompanyBase(AbcallUserBase):
    greeting: str
    farewell: str

class CompanyCreate(BaseModel):
    name: str
    first_name: str
    last_name: str
    birth_date: date
    phone_number: str
    country: str
    city: str
    username: EmailStr
    password: str

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

class CompanyUpdate(AbcallUserUpdate):
    greeting: Optional[str] = None
    farewell: Optional[str] = None

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

class UserBase(AbcallUserBase):
    identification_number: str
    phone: str
    email: str
    opinions: List[str]
    importance: int
    allows_calls: bool
    allows_sms: bool
    allows_email: bool

class UserCreate(UserBase):
    pass

class UserUpdate(AbcallUserUpdate):
    identification_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    opinions: Optional[List[str]] = None
    importance: Optional[int] = None
    allows_calls: Optional[bool] = None
    allows_sms: Optional[bool] = None
    allows_email: Optional[bool] = None

class UserResponse(UserBase):
    pass

class ManagerBase(AbcallUserBase):
    pass

class ManagerCreate(ManagerBase):
    pass

class ManagerUpdate(AbcallUserUpdate):
    pass

class ManagerResponse(ManagerBase):
    pass