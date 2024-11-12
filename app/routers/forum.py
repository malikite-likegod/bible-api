from fastapi import status, HTTPException, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas, utils, oauth2
import time
from ..database import get_db

router = APIRouter(
    prefix="/forum",
    tags=['Forum']
)


@router.post("/categories/", status_code=status.HTTP_201_CREATED)
async def create_category(category: schemas.CategoryCreate,db: Session = Depends(get_db)):
    new_category = models.Category(name=category.name, description=category.description)
    db.add(new_category)
    await db.commit()
    return new_category

@router.get("/categories/")
async def list_categories(db: Session = Depends(get_db)):
    categories = await db.execute("SELECT * FROM categories")
    return categories.scalars().all()

### Forum Threads
@router.post("/threads/", status_code=status.HTTP_201_CREATED)
async def create_thread(thread: schemas.ThreadCreate, current_user: int =  Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    category = await db.get(models.Category, thread.category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    new_thread = models.Thread(title=thread.title, category_id=thread.category_id, author_id=current_user.id)
    db.add(new_thread)
    await db.commit()
    return new_thread

@router.get("/categories/{category_id}/threads/")
async def list_threads(category_id: int, db: Session = Depends(get_db)):
    threads = await db.execute("SELECT * FROM threads WHERE category_id = :category_id", {"category_id": category_id})
    return threads.scalars().all()

### Forum Posts
@router.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: schemas.PostCreate,  current_user: int =  Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    thread = db.get(models.Thread, post.thread_id)
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
    
    new_post = models.ForumPost(content=post.content, thread_id=post.thread_id, author_id=current_user.id)
    db.add(new_post)
    await db.commit()
    return new_post

@router.get("/threads/{thread_id}/posts/")
async def list_posts(thread_id: int, db: Session = Depends(get_db)):
    posts = await db.execute("SELECT * FROM posts WHERE thread_id = :thread_id", {"thread_id": thread_id})
    return posts.scalars().all()

### Forum Comments
@router.post("/comments/", status_code=status.HTTP_201_CREATED)
async def create_comment(comment: schemas.CommentCreate, current_user: int =  Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    post = await db.get(models.ForumPost, comment.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    new_comment = models.Comment(content=comment.content, post_id=comment.post_id, author_id=current_user.id)
    db.add(new_comment)
    await db.commit()
    return new_comment

@router.get("/posts/{post_id}/comments/")
async def list_comments(post_id: int, db: Session = Depends(get_db)):
    comments = await db.execute("SELECT * FROM comments WHERE post_id = :post_id", {"post_id": post_id})
    return comments.scalars().all()


@router.delete("/threads/{thread_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(thread_id: int, current_user: int =  Depends(oauth2.get_current_user), db: Session = Depends(get_db)):
    # Check if the current user is an admin or the thread owner
    thread = await db.get(models.Thread, thread_id)
    if not thread or (thread.author_id != current_user.id and not current_user.is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this thread")

    await db.delete(thread)
    await db.commit()

# @router.delete("/posts/{post_id}/", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_post(post_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(SessionLocal)):
#     # Check if the current user is an admin or the post owner
#     post = await db.get(Post, post_id