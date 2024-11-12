from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime, Text, Enum
from sqlalchemy.sql.sqltypes import TABLEVALUE, TIMESTAMP
from sqlalchemy.sql.expression import text, func
from sqlalchemy.orm import relationship
import enum


class PrivilegeLevel(enum.Enum):
    admin = "admin"
    moderator = "moderator"
    contributor = "contributor"
    user = "user"

PrivilegeLevelType: Enum = Enum(
    PrivilegeLevel,
    name="privilegeLevel",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_private = Column(Boolean, default=False)
    location = Column(String, nullable=True)
    relationship_status = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    privilege_level = Column(Enum(PrivilegeLevel), unique=False, nullable=False)

    followers = relationship("Follow", back_populates="followed", foreign_keys="[Follow.followed_id]")
    following = relationship("Follow", back_populates="follower", foreign_keys="[Follow.follower_id]")
    posts = relationship("Post", back_populates="owner")
    postimages = relationship("PostImage", back_populates="user")
    messages = relationship("Message", back_populates="user")
    group_memberships = relationship("GroupMembership", back_populates="user")
    wall_posts = relationship("WallPost", back_populates="author")
    activities = relationship("Activity", back_populates="user")

class Follow(Base):
    __tablename__ = "follows"
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    followed_id = Column(Integer, ForeignKey("users.id"))
    follower = relationship("User", back_populates="following", foreign_keys=[follower_id])
    followed = relationship("User", back_populates="followers", foreign_keys=[followed_id])


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_path = Column(String)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User")

class WallPost(Base):
    __tablename__ = "wall_posts"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    author = relationship("User", back_populates="wall_posts")

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user = relationship("User", back_populates="activities")

class Language(Base):

    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, nullable=False)
    language_name = Column(String, nullable=False, unique=True)



class Translation(Base):

    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    language_id = Column(Integer, ForeignKey("languages.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, default=1)

    language = relationship("Language")


class Book(Base):

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, nullable=False)
    sequence = Column(Integer, nullable=False, unique=True)



class BookTitle(Base):

    __tablename__ = "bookstitles"

    id = Column(Integer, primary_key=True, nullable=False)
    label = Column(String, nullable=False, unique=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id", ondelete="CASCADE"), nullable=False)

    language = relationship("Language")
    book = relationship("Book")


class Chapter(Base):

    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, nullable=False)
    number = Column(Integer, nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    book = relationship("Book")

    UniqueConstraint("book_id", "number", name="unique_chapter")

class ChapterNote(Base):

    __tablename__ = "chapter_notes"

    id = Column(Integer, primary_key=True, nullable=False)
    note_text = Column(String, nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    UniqueConstraint("user_id", "chapter_id", name="unique_chapter_note")


class Verse(Base):
     
    __tablename__ = "verses"

    id = Column(Integer, primary_key=True, nullable=False)
    number = Column(Integer, nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    book = relationship("Chapter") 

    UniqueConstraint("chapter_id", "number", name="unique_verse")


class VerseLabel(Base):

    __tablename__ = "verselabels"

    id = Column(Integer, primary_key=True, nullable=False)
    text = Column(String, nullable=False)
    verse_id = Column(Integer, ForeignKey("verses.id", ondelete="CASCADE"), nullable=False)
    translation_id = Column(Integer, ForeignKey("translations.id", ondelete="CASCADE"), nullable=False)
    verse = relationship("Verse")

    UniqueConstraint("verse_id", "translation_id", name="unique_translation_label")


class VerseNote(Base):
    __tablename__ = "versenotes"

    id = Column(Integer, primary_key=True, nullable=False)
    note_text = Column(String, nullable=False)
    verse_id = Column(Integer, ForeignKey("verses.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    UniqueConstraint("verse_id", "author_id", name="unique_verse_note")



class BookGrouping(Base):
    __tablename__ = "bookgroupings"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)


class BookGroupEntry(Base):
    __tablename__ = "bookgroup_entries"

    id = Column(Integer, primary_key=True, nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    book_group_id = Column(Integer, ForeignKey("bookgroupings.id", ondelete="CASCADE"), nullable=False)

    UniqueConstraint("book_id", "book_group_id", name="unique_book_group_entry")


# Token database model
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    jti = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    expires_at = Column(DateTime)
    blacklisted = Column(Boolean, default=False)


#Chat Tables
class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    is_group = Column(Boolean, default=False)
    name = Column(String, nullable=True)
    messages = relationship("Message", back_populates="chat")
    group_memberships = relationship("GroupMembership", back_populates="chat")



class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(Integer, ForeignKey("chats.id"))
    # relationships
    user = relationship("User", back_populates="messages")
    chat = relationship("Chat", back_populates="messages")

class GroupMembership(Base):
    __tablename__ = "group_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(Integer, ForeignKey("chats.id"))
    # relationships
    user = relationship("User", back_populates="group_memberships")
    chat = relationship("Chat", back_populates="group_memberships")



class PostImage(Base):
    __tablename__ = "postimages"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    image_path = Column(String)
    user = relationship("User", back_populates="postimages")



######################## forum models

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    threads = relationship("Thread", back_populates="category")

class Thread(Base):
    __tablename__ = "threads"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    category_id = Column(Integer, ForeignKey("categories.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    
    category = relationship("Category", back_populates="threads")
    forumposts = relationship("ForumPost", back_populates="thread")
    author = relationship("User")

class ForumPost(Base):
    __tablename__ = "forumposts"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    thread_id = Column(Integer, ForeignKey("threads.id"))
    author_id = Column(Integer, ForeignKey("users.id"))

    thread = relationship("Thread", back_populates="forumposts")
    comments = relationship("Comment", back_populates="forumpost")
    author = relationship("User")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    forumpost_id = Column(Integer, ForeignKey("forumposts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))

    forumpost = relationship("ForumPost", back_populates="comments")
    author = relationship("User")


    ###### Article tables

    class Document(Base):
        __tablename__ = "documents"
        id = Column(Integer, primary_key=True, index=True)
        title = Column(String, nullable=False)
        created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
        content = Column(Text)  # HTML content stored as text
        published = Column(Boolean, default=False)
        user_id = Column(Integer, ForeignKey("users.id"))