from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

from . import schemas, database, models
from .config import settings

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})


    encoded_jwt =  jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# give database access to grab user information
async def create_refresh_token(data: dict, db: Session = Depends(database.get_db)):
    to_encode = data.copy()
    refresh_id = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)



    to_encode.update({"exp": expire, "jti": refresh_id})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # write to database
    
    # Store refresh token in the database
    db_token = models.RefreshToken(
        token=token,
        jti=refresh_id,
        user_id=data["user_id"],
        expires_at=expire,
        blacklisted=False
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return token


def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: int = payload.get("user_id")

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    
    except InvalidTokenError:
        raise credentials_exception 
    
    return token_data



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = verify_access_token(token , credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if current_user.privilege_level not in {models.PrivilegeLevel.admin, models.PrivilegeLevel.moderator, models.PrivilegeLevel.user}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return current_user


# need function to check to see if user has access to protected content