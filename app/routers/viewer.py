from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas, utils, oauth2
import time
from ..database import get_db

router = APIRouter(
    prefix="/viwer",
    tags=['Viewer']
)


@router.get("/books/{book_id}", response_model=schemas.Booktitle)
def get_book(db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user), language_id: int = 24, book_id: int= 271):

    booktitle = db.query(models.BookTitle).filter(models.BookTitle.book_id == book_id, models.BookTitle.language_id == language_id).first()
    
    return booktitle


@router.get("/books")
def get_book(db: Session = Depends(get_db), current_user: int =  Depends(oauth2.get_current_user), language_id: int = 24):

    booktitle = db.query(models.BookTitle).filter(models.BookTitle.language_id == language_id).all()
    
    return booktitle


@router.get("/languages")
def get_languages(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    languages = db.query(models.Language).all()
            

    return languages


@router.get("/translations")
def get_translations(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), language_id: int = 24):
    
    translations = db.query(models.Translation).filter(models.Translation.language_id == language_id).all()


    return translations  


@router.get("/chapterview")
def get_chapterview(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), translation_id: int = 1, chapter_id: int = 1):

    chapter_query = db.query(models.Verse, models.VerseLabel).join(models.VerseLabel).filter(models.Verse.chapter_id == chapter_id).all()


    if not chapter_query :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="chapter or translation could not be found")


    joined_data = [
        {
            "verse": {
                "id": row.Verse.id,
                "number": row.Verse.number,
                "chapter": row.Verse.chapter_id,
            },
            "VerseLabel": {
                "text": row.VerseLabel.text,
                "translation_id": row.VerseLabel.translation_id
            }
        }
        for row in chapter_query
    ]

    return {"chapter_data": joined_data}