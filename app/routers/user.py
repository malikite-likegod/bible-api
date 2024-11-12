from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
import time
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    #check passord complexity
    if utils.is_password_complexity_valid(user.password):

        #hash password - user.password
        hashed_password = utils.hash(user.password)
        user.password = hashed_password
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, details="password complexity does not follow guidelines")
        
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user  


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} not found")
    
    return user