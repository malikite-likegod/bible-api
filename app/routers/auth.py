from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, OAuth2PasswordBearer 
from sqlalchemy.orm import Session
import jwt


from .. import schemas, database, models, utils, oauth2
from .. config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(
    tags=['Authentication']
)

@router.post('/login', response_model=schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)) :

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
    
    #create token
    access_token = oauth2.create_access_token(data={"user_id" : user.id})
    refresh_token = await oauth2.create_refresh_token(data={"user_id" : user.id}, db=db)
    #return token
    return {"access_token" : access_token, "refresh_token" : refresh_token, "token_type" : "bearer"}



@router.post('/refresh', response_model=schemas.Token)
async def refresh_token(refresh_token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):

    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=settings.algorithm)
        refresh_id: str = payload.get("jti")
        user_id = payload.get("user_id")

        print ("jti: " + refresh_id)
        print (user_id)

        if not user_id or not refresh_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Find the token in the database
        db_token = db.query(models.RefreshToken).filter(models.RefreshToken.jti == refresh_id, models.RefreshToken.user_id == user_id).first()
        if not db_token or db_token.blacklisted:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is blacklisted or invalid")

        # Blacklist the old refresh token
        db_token.blacklisted = True
        db.commit()

        # Create new tokens
        new_access_token = oauth2.create_access_token(data={"user_id": user_id})
        new_refresh_token = await oauth2.create_refresh_token(data={"user_id": user_id}, db=db)

        return {"access_token" : new_access_token, "refresh_token" : new_refresh_token, "token_type" : "bearer"}
    except jwt.exceptions.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

#need path to refresh token