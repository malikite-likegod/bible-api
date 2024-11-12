from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas, utils, oauth2
from . import chat_crud as crud
import time
from typing import List
from ..database import get_db

router = APIRouter(
    prefix="/chats",
    tags=['Chat']
)



@router.post("/chats/", response_model=schemas.Chat)
def create_chat(chat: schemas.ChatCreate, db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    db_chat = crud.create_chat(db, chat)
    return db_chat


# check to make sure that other users account is not private and if so only mutual friends can chat
@router.post("/chats/{chat_id}/users/{user_id}")
def add_user_to_chat(chat_id: int, db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    membership = crud.add_user_to_chat(db, user_id=current_user, chat_id=chat_id)
    return {"status": "user added"}


#check if user is a participant before posting
@router.post("/messages/", response_model=schemas.Message)
def send_message(message: schemas.MessageCreate, db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    db_message = crud.create_message(db, message, current_user)
    return db_message

#need to check if user is a participant in chat before returning
@router.get("/chats/{chat_id}/messages", response_model=List[schemas.Message])
def get_chat_messages(chat_id: int, db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    messages = db.query(models.Message).filter(models.Message.chat_id == chat_id).order_by(models.Message.timestamp).all()
    return messages