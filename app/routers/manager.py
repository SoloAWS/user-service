from fastapi import APIRouter, Depends, Header, Query, Path, HTTPException
from sqlalchemy.orm import Session
from ..schemas.user import AbcallUserCreate, ManagerResponse
from ..models.model import Manager, ABCallUser, save_user
from ..session import get_db
from uuid import UUID
import jwt
import os

router = APIRouter(prefix="/user/manager", tags=["Manager"])

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

@router.post("/", response_model=ManagerResponse, status_code=201)
def create_manager(manager: AbcallUserCreate, db: Session = Depends(get_db)):
    existing_manager = db.query(ABCallUser).filter(ABCallUser.username == manager.username).first()
    if existing_manager:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    created_manager = save_user(db, Manager, manager)
    return created_manager

@router.get("/{manager_id}", response_model=ManagerResponse)
def get_manager(manager_id: UUID = Path(...), db: Session = Depends(get_db), 
                #current_user: dict = Depends(get_current_user)
                ):
    #if current_user['user_type'] != 'manager':
    #    raise HTTPException(status_code=403, detail="Not authorized to view manager details")

    manager = db.query(Manager).filter(Manager.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    return manager
