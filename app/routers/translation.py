from fastapi import status, HTTPException, Response, Depends, APIRouter, File, UploadFile
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from .. import models, schemas, utils, oauth2, database
import time
import shutil
import lxml
from bs4 import BeautifulSoup as soup

import sys, os




router = APIRouter(
    prefix="/translations",
    tags=['Translation Upload']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_translation(language: str, translation: str, file: UploadFile=File(...), current_user: int =  Depends(oauth2.get_current_user),  db: Session = Depends(database.get_db)):

    if not file:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Not a valid file")
    else:
        try:
            path =f"versions/{file.filename}"
            with open(path, 'w+b') as buffer:
                shutil.copyfileobj(file.file, buffer)

            with open(path) as f:
                contents = f.read()

                
                new_language = models.Language(language_name=language)

                lang_check = db.query(models.Language).filter_by(language_name=language).first()

                if not lang_check:
                    db.add(new_language)
                    db.commit()
                    db.refresh(new_language)
                else:
                    new_language = lang_check

                new_translation = models.Translation(name = translation, language_id = new_language.id, author_id = current_user.id)

                trans_check = db.query(models.Translation).filter_by(name = translation, language_id = new_language.id).first()

                if not trans_check:

                    db.add(new_translation)
                    db.commit()
                    db.refresh(new_translation)
                

                    #print (contents)

                    page_soup = soup(contents, "lxml")

                    xmlbible = page_soup.find_all("xmlbible")

                    current_verse_number = 0
                
                    for bible in xmlbible:

                        books = page_soup.find_all("biblebook")

                        for book in books:

                            bookname = book['bname']
                            booknum = book['bnumber']
                            #print("testing addbook argument: " + booknum)

                            #book_object = addBook({"sequence": booknum})
                            new_book = models.Book(sequence = booknum)

                            book_check = db.query(models.Book).filter_by(sequence = booknum).first()

                            if not book_check:

                                db.add(new_book)
                                db.commit()
                                db.refresh(new_book)
                            else:
                                new_book = book_check

                            booktitle = models.BookTitle(book_id = new_book.id, label = bookname, language_id = new_language.id)

                            booktitle_check = db.query(models.BookTitle).filter_by(label = bookname, language_id=new_language.id).first()

                            if not booktitle_check:

                                db.add(booktitle)
                                db.commit()
                                db.refresh(booktitle)
                            else:
                                booktitle = booktitle_check

                            #booktitle_object = addBookTitle({"book_id": book_object.id, "language_id": translation.language_id, "label": bookname})

                            chaps = book.findChildren("chapter", recursive="false")

                            for chapter in chaps:
                                chapternum = chapter['cnumber']

                                #chapter_object = addChapter({"book_id": book_object.id, "number": chapternum})
                                new_chapter = models.Chapter(book_id = new_book.id, number = chapternum)

                                chapter_check = db.query(models.Chapter).filter_by(book_id=new_book.id, number = chapternum).first()

                                if not chapter_check:

                                    db.add(new_chapter)
                                    db.commit()
                                    db.refresh(new_chapter)
                                else:
                                    new_chapter = chapter_check

                                verses = chapter.findChildren("vers", recursive="false")

                                for verse in verses:
                                    versenum = verse['vnumber']
                                    #v = addVerse({"chapter_id": chapter_object.id, "number": versenum})

                                    current_verse_number += 1
                                    match current_verse_number:

                                        case 1555:
                                            print("5 percent")
                                        case 3110:
                                            print("10 percent")
                                        case 6220:
                                            print("20 percent")
                                        case 9330:
                                            print("30 percent")
                                        case 15551:
                                            print("50 percent")
                                        case 23327:
                                            print("75 percent")
                                        case 27992:
                                            print("90 percent")

                                    new_verse = models.Verse(chapter_id = new_chapter.id, number = versenum)

                                    verse_check = db.query(models.Verse).filter_by(chapter_id = new_chapter.id, number = versenum).first()

                                    if not verse_check:

                                        db.add(new_verse)
                                        db.commit()
                                        db.refresh(new_verse)
                                    else:
                                        new_verse = verse_check

                                    verse_label = verse.get_text()

                                    # print(new_translation.id)
                                    # print(new_verse.id)
                                    # print(verse_label)

                                    new_verselabel = models.VerseLabel(translation_id = new_translation.id, verse_id = new_verse.id, text = verse_label)

                                    verse_label_check = db.query(models.VerseLabel).filter_by(translation_id = new_translation.id, verse_id = new_verse.id, text = verse_label).first()

                                    if not verse_label_check:
                                        db.add(new_verselabel)
                                        db.commit()
                                        db.refresh(new_verselabel)

                                    #vtext = addVerseLabel({"verse_id": v.id, "translation_id": translation.id, "label": verse_label})
                else:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"The Translation: {translation} has previously already been added")
            # # db_session.set(db)
            # # new_language = schemas.Language(language_name=language)
            # # lang = translation_load.addLanguage(new_language)
            # # translation_data = {"name": translation, "language_id": lang.id}
            # # new_translation = schemas.Translation(translation_data)
            # # trans = translation_load.addTranslation(new_translation)
            # # translation_load.loadTranslation(trans, contents)
            print("complete")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(f"An exception of type {exc_type.__name__} occurred. Details: {exc_obj}")
            return JSONResponse(content=f"Something went wrong processing the file :: {exc_obj}", status_code=500)
        finally:
            file.file.close()

        return new_translation