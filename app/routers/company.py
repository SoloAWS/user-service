from fastapi import APIRouter, Depends, Header, Path, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas.user import CompanyCreate, CompanyIdsRequest, CompanyResponse, CompanyPlanRequest
from ..models.model import Company, ABCallUser, save_user
from ..session import get_db
from uuid import UUID
import jwt
import os

router = APIRouter(prefix="/user/company", tags=["Company"])

SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'secret_key')
ALGORITHM = "HS256"

def get_current_user(token: str = Header(None)):
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

@router.post("/", response_model=CompanyResponse, status_code=201)
def create_company(company_schema: CompanyCreate, db: Session = Depends(get_db)):
    if db.query(ABCallUser).filter(ABCallUser.username == company_schema.username).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    created_company = save_user(db, Company, company_schema)
    return created_company

@router.get("/{company_id}", response_model=CompanyResponse, status_code=200)
def view_company(
    company_id: UUID = Path(..., description="Id of the company"),
    db: Session = Depends(get_db),
    #current_user: dict = Depends(get_current_user)
):
    #if not current_user:
    #    raise HTTPException(status_code=401, detail="Authentication required")
    
    #if current_user['user_type'] not in ['manager', 'company']:
    #    raise HTTPException(status_code=403, detail="Not authorized to view companies")
    
    #if current_user['user_type'] == 'company' and str(current_user['sub']) != str(company_id):
    #    raise HTTPException(status_code=403, detail="Not authorized to view this company")
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/assign-plan", response_model=dict, status_code=200)
def assign_plan_to_user(
    company_plan_info: CompanyPlanRequest,
    db: Session = Depends(get_db),
    #current_user: dict = Depends(get_current_user)
):
    #if not current_user and current_user['sub'] != company_plan_info.company_id:
     #   raise HTTPException(status_code=401, detail="Authentication required")
    
    company = db.query(Company).filter(
        Company.id == company_plan_info.company_id,
    ).first()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.plan_id = company_plan_info.plan_id
    db.commit()

    return {"message": "Plan assigned successfully"}


@router.post("/get-by-id", response_model=List[dict], status_code=200)
def get_companies(
    company_ids_request: CompanyIdsRequest,
    db: Session = Depends(get_db),
    #current_user: dict = Depends(get_current_user)
):
    
    #if not current_user:
     #   raise HTTPException(status_code=401, detail="Authentication required")
     
    #if current_user['user_type'] != 'manager':
    #    raise HTTPException(status_code=403, detail="Not authorized to view companies")
    if not company_ids_request.company_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one company ID must be provided"
        )
    
    try:
        company_ids = [UUID(id_str) for id_str in company_ids_request.company_ids]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format in company_ids"
        )
    
    companies = db.query(Company).filter(Company.id.in_(company_ids)).all()
    
    if not companies:
        raise HTTPException(status_code=404, detail="No companies found")

    company_map = {str(company.id): {"company_id": company.id, "name": company.name} 
                  for company in companies}
    
    ordered_results = []
    for company_id in company_ids_request.company_ids:
        company_data = company_map.get(company_id)
        if company_data:
            ordered_results.append(company_data)
    
    return ordered_results