from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class ABCallUser(Base):
    __tablename__ = "abcall_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    
    type = Column(String(50))

    __mapper_args__ = {
        "polymorphic_identity": "abcall_user",
        "polymorphic_on": type
    }

class Company(ABCallUser):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), ForeignKey('abcall_users.id'), primary_key=True)
    name = Column(String, nullable=False)
    greeting = Column(String, nullable=True)
    farewell = Column(String, nullable=True)
    birth_date = Column(Date, nullable=False)
    phone_number = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "company",
    }
    
def save_user(db, user_model, user_data):
    db_user = user_model(**user_data.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user