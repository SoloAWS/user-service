from fastapi import APIRouter, Depends, Header, Path, HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import CompanyCreate, CompanyResponse, CompanyPlanRequest
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
        raise HTTPException(status_code=404, detail="User not found")

    company.plan_id = company_plan_info.plan_id
    db.commit()

    return {"message": "Plan assigned successfully"}