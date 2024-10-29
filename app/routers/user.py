# app/routers/user.py
from fastapi import APIRouter, Depends, Header, Query, Path, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..schemas.user import UserCreate, UserResponse, UserDocumentInfo, UserCompaniesResponse, UserIdRequest
from ..models.model import User, Company, ABCallUser, company_user_association
from ..session import get_db
from uuid import UUID
import jwt
import os

router = APIRouter(prefix="/user/user", tags=["User"])

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

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user_schema: UserCreate, db: Session = Depends(get_db)):
    association = db.query(company_user_association).filter(
        company_user_association.c.document_type == user_schema.document_type,
        company_user_association.c.document_id == user_schema.document_id
    ).first()

    if not association:
        raise HTTPException(status_code=400, detail="The given user does not belong to any registered company")

    if db.query(ABCallUser).filter(ABCallUser.username == user_schema.username).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_user = db.query(User).filter(
        User.document_type == user_schema.document_type,
        User.document_id == user_schema.document_id
    ).first()

    if existing_user:
        for key, value in user_schema.dict().items():
            setattr(existing_user, key, value)
        db.commit()
        db.refresh(existing_user)
        return existing_user
    else:
        raise HTTPException(status_code=404, detail="User to update not found")

@router.get("/{user_id}", response_model=UserResponse, status_code=200)
def view_user(
    user_id: UUID = Path(..., description="Id of the user"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
       raise HTTPException(status_code=401, detail="Authentication required")
    
    if current_user['user_type'] not in ['manager', 'company']:
       raise HTTPException(status_code=403, detail="Not authorized to view users")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user['user_type'] == 'company':

        association = db.query(company_user_association).filter(
            company_user_association.c.company_id == current_user['sub'],
            company_user_association.c.user_id == user_id
        ).first()
        if not association:
            raise HTTPException(status_code=403, detail="Not authorized to view this user")

    return user

@router.post("/companies", response_model=UserCompaniesResponse)
def get_user_companies(
    user_doc_info: UserDocumentInfo,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
       raise HTTPException(status_code=401, detail="Authentication required")
    
    user = db.query(User).filter(
        User.document_type == user_doc_info.document_type,
        User.document_id == user_doc_info.document_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user['user_type'] == 'user':
        if str(current_user['sub']) != str(user.id):
            raise HTTPException(status_code=403, detail="Not authorized to view this user's companies")
    elif current_user['user_type'] == 'company':
        raise HTTPException(status_code=403, detail="Not authorized to view user companies")

    companies = db.query(Company).join(
        company_user_association,
        and_(
            company_user_association.c.company_id == Company.id,
            company_user_association.c.user_id == user.id
        )
    ).all()

    return UserCompaniesResponse(user_id=user.id, companies=companies)

@router.post("/companies-user", response_model=UserCompaniesResponse)
def get_user_companies(
    user_doc_info: UserIdRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
       raise HTTPException(status_code=401, detail="Authentication required")
    
    user = db.query(User).filter(
        User.id == user_doc_info.id,
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user['user_type'] == 'user':
       if str(current_user['sub']) != str(user.id):
           raise HTTPException(status_code=403, detail="Not authorized to view this user's companies")
    elif current_user['user_type'] == 'company':
       raise HTTPException(status_code=403, detail="Not authorized to view user companies")

    companies = db.query(Company).join(
        company_user_association,
        and_(
            company_user_association.c.company_id == Company.id,
            company_user_association.c.user_id == user.id
        )
    ).all()

    return UserCompaniesResponse(user_id=user.id, companies=companies)