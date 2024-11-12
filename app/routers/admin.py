from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas, utils, oauth2
import time
from ..database import get_db

router = APIRouter(
    prefix="/admin",
    tags=['Administration']
)


@router.post("/users/", response_model=schemas.UserCreate)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_active_user)):
    if current_user.privilege_level != models.PrivilegeLevel.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email address already registered")
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(username=user.email, password_hash=hashed_password, privilege_level=user.privilege_level)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Edit account: Lock, unlock, change password


@router.get("/protected/admin")
def read_protected_admin(current_user: models.User = Depends(oauth2.get_current_user)):
    if current_user.privilege_level != models.PrivilegeLevel.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return {"msg": "Hello, Admin!"}

@router.get("/protected/moderator")
def read_protected_moderator(current_user: models.User = Depends(oauth2.get_current_user)):
    if current_user.privilege_level not in {models.PrivilegeLevel.admin, models.PrivilegeLevel.moderator}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Moderator privileges required")
    return {"msg": "Hello, Moderator!"}


@router.get("/protected/contributor")
def read_protected_contributor(current_user: models.User = Depends(oauth2.get_current_user)):
    if current_user.privilege_level not in {models.PrivilegeLevel.admin, models.PrivilegeLevel.moderator, models.PrivilegeLevel.contributor}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contributor privileges required")
    return {"msg": "Hello, Contributor!"}