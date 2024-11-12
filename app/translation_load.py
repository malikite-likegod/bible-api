from fastapi import Depends
from sqlalchemy.orm import Session
import lxml
from bs4 import BeautifulSoup as soup
from . import schemas, models
from .database import get_db, db_session




def addBookTitle(title: schemas.Booktitle, db: Session):
       

        booktitle = models.BookTitle(**title.model_dump())

        db.add(booktitle)
        db.commit()
        db.refresh(booktitle)

        return booktitle


def addBook(book: schemas.Book):
        
        new_book = models.Book(**book.model_dump())

        db.add(new_book)
        db.commit()
        db.refresh(new_book)

        return new_book


def addChapter(chapter: schemas.Chapter):
        
        new_chapter = models.Chapter(**chapter.model_dump())

        db.add(new_chapter)
        db.commit()
        db.refresh(new_chapter)

        return new_chapter


def addVerse(verse: schemas.Verse):
        
        new_verse = models.Verse(**verse.model_dump())

        db.add(new_verse)
        db.commit()
        db.refresh(new_verse)

        return new_verse

def addVerseLabel(verselabel: schemas.VerseLabel):
        
        new_verselabel = models.Verselabel(**verselabel.model_dump())

        db.add(new_verselabel)
        db.commit()
        db.refresh(new_verselabel)

        return new_verselabel

def addLanguage(language: schemas.Language):

        print ("entered addLanguage")
        new_language = models.Language(**language.model_dump())

        db.add(new_language)
        db.commit()
        db.refresh(new_language)

        return new_language

def addTranslation(translation: schemas.Translation):

        new_translation = models.Translation(**translation.model_dump())

        db.add(new_translation)
        db.commit()
        db.refresh(new_translation)

        return new_translation


def loadTranslation(translation: schemas.TranslationOut, filedata):

        version =''

        for line in filedata:
                 version +=line

        page_soup = soup(version, "lxml-xml")

        books = page_soup.find_all("biblebook")

        for book in books:

                bookname = book['bname']
                booknum = book['bnumber']
                print("testing addbook argument: " + booknum)

                book_object = addBook({"sequence": booknum})

                booktitle_object = addBookTitle({"book_id": book_object.id, "language_id": translation.language_id, "label": bookname})

                chaps = book.findChildren("chapter", recursive="false")

                for chapter in chaps:
                        chapternum = chapter['cnumber']
                        chapter_object = addChapter({"book_id": book_object.id, "number": chapternum})

                        verses = chapter.findChildren("vers", recursive="false")

                        for verse in verses:
                                versenum = verse['vnumber']
                                v = addVerse({"chapter_id": chapter_object.id, "number": versenum})
                                verse_label = verse.get_text()

                                vtext = addVerseLabel({"verse_id": v.id, "translation_id": translation.id, "label": verse_label})
