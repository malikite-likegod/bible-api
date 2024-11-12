from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from typing_extensions import Annotated
from .models import PrivilegeLevel


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    privilege_level: PrivilegeLevel

class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    privilege_level: PrivilegeLevel


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None


class Booktitle(BaseModel):
    label: str
    book_id: int
    language_id: int

    class Config:
        from_attributes = True

class Book(BaseModel):
    sequence: int


class Chapter(BaseModel):
    number: int
    book_id: int


class Verse(BaseModel):
    chapter_id: int
    number: int


class VerseLabel(BaseModel):
    verse_id: int
    translation_id: int
    label: str


class VerseOut(BaseModel):
    id: int
    chapter_id: int
    number: int
    translation_id: int
    label: str

    class Config:
        from_attributes = True


class Language(BaseModel):
    language_name: str

class Translation(BaseModel):
    name: str
    language_id: int

class TranslationOut(BaseModel):
    id: int
    name: str
    language_id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CreateTranslation(BaseModel):
    language_id: int
    translation_name: str
    

class MessageBase(BaseModel):
    content: str
    chat_id: int

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: datetime
    user_id: int
    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    is_group: bool
    name: Optional[str] = None

class ChatCreate(ChatBase):
    pass

class Chat(ChatBase):
    id: int
    members: List[UserOut] = []
    messages: List[Message] = []
    class Config:
        from_attributes = True


class FollowUser(BaseModel):
    follower_id: int
    followed_id: int


class ProfileUpdate(BaseModel):
    location: Optional[str] = None
    relationship_status: Optional[str] = None
    bio: Optional[str] = None

class WallPostCreate(BaseModel):
    content: str


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ThreadCreate(BaseModel):
    title: str
    category_id: int

class PostCreate(BaseModel):
    content: str
    thread_id: int

class CommentCreate(BaseModel):
    content: str
    post_id: int


class DocumentCreate(BaseModel):
    title: str
    user_id: int
    content: str  # Accept HTML content

class DocumentResponse(BaseModel):
    id: int
    title: str
    user_id: int
    content: str