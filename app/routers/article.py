from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas, utils, oauth2
from . import chat_crud as crud
import time
from typing import List
from ..database import get_db

router = APIRouter(
    prefix="/documents",
    tags=['Articles']
)



@router.post("/documents/", response_model=schemas.DocumentResponse)
def create_document(doc: schemas.DocumentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    if current_user.privilege_level not in {models.PrivilegeLevel.admin, models.PrivilegeLevel.moderator, models.PrivilegeLevel.contributor}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contributor privileges required")

    new_doc = models.Document(title=doc.title, content=doc.content, user_id=current_user.id)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    db.close()
    return new_doc


##############   need routes

### publish - moderator and up
### unpublish - moderator and up
## edit - author
## delete - moderator and up


@router.get("/documents/{doc_id}", response_model=schemas.DocumentResponse)
def read_document(doc_id: int,  db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    db.close()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc

@router.get("/documents/{doc_id}/html")
def document_to_html(doc_id: int, db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user)):
    
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    db.close()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    # HTML content is already stored in `content`, so return it directly
    return {"html": doc.content}