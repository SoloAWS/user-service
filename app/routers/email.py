# app/routers/email.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from ..models.model import User, Company, ABCallUser, company_user_association
from ..session import get_db
from pydantic import BaseModel
import logging
from typing import Optional
from uuid import UUID

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/user/email", tags=["Email"])

class CompanySearchResponse(BaseModel):
    id: UUID
    name: str

class UserValidationResponse(BaseModel):
    id: UUID
    email: str
    company_id: UUID
    company_name: str

@router.get("/company", response_model=CompanySearchResponse)
def search_company_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    """Search company by name"""
    try:
        company = db.query(Company).filter(
            func.lower(Company.name) == func.lower(name)
        ).first()
        
        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company with name '{name}' not found"
            )
        
        return CompanySearchResponse(
            id=company.id,
            name=company.name
        )
    except Exception as e:
        logger.error(f"Error searching company: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while searching company"
        )

@router.get("/validate", response_model=UserValidationResponse)
def validate_user_company(
    email: str,
    company_id: UUID,
    db: Session = Depends(get_db)
):
    """Validate user email belongs to company"""
    # First find the user by email
    user = db.query(User).filter(User.username == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Then check if this user is associated with the specified company
    company = db.query(Company).join(
        company_user_association,
        and_(
            company_user_association.c.company_id == company_id,
            company_user_association.c.user_id == user.id
        )
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="User does not belong to this company")

    return UserValidationResponse(
        id=user.id,
        email=user.username,
        company_id=company.id,
        company_name=company.name
    )