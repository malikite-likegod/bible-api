from sqlalchemy.orm import Session
from .. import models, schemas
from sqlalchemy.exc import IntegrityError

def create_chat(db: Session, chat: schemas.ChatCreate):
    db_chat = models.Chat(is_group=chat.is_group, name=chat.name)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def add_user_to_chat(db: Session, user_id: int, chat_id: int):
    membership = models.GroupMembership(user_id=user_id, chat_id=chat_id)
    db.add(membership)
    db.commit()
    return membership

def create_message(db: Session, message: schemas.MessageCreate, user_id: int):
    db_message = models.Message(content=message.content, chat_id=message.chat_id, user_id=user_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message