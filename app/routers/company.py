from fastapi import APIRouter, Depends, Header, Query, Path, HTTPException

from ..schemas.user import CompanyCreate, CompanyResponse
from ..models.model import Company, save_user

from sqlalchemy.orm import Session
from ..session import get_db

from uuid import UUID

router = APIRouter(prefix="/company", tags=["Company"])

@router.post("/", response_model=CompanyResponse, status_code=201)
def create_company(company_schema: CompanyCreate, db: Session = Depends(get_db)):
    if db.query(Company).filter(Company.username == company_schema.username).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    created_company = save_user(db, Company, company_schema)
    return created_company

@router.get("/{company_id}", response_model=CompanyResponse, status_code=200)
def view_companies(
    company_id: UUID = Path(..., description="Id of the offer"),
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company