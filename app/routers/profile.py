from fastapi import status, HTTPException, status,File, UploadFile, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas, utils, oauth2
from . import chat_crud as crud
import time
from typing import List
from ..database import get_db
import os
import shutil

router = APIRouter(
    tags=['Profile']
)   


@router.post("/follow/")
async def follow_user(follow: schemas.FollowUser, db: Session = Depends(get_db)):
    # Check if user is private and add follow request or follow directly
    pass

@router.post("/upload/")
async def upload_image(file: UploadFile = File(...), current_user: int =  Depends(oauth2.get_current_user)):
    # Save the image to a directory and store path in database
    upload_dir = "uploads/"
    os.makedirs(upload_dir, exist_ok=True)
    file_location = f"{upload_dir}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Save file path to database
    post = models.PostImage(owner_id=current_user.id, image_path=file_location)
    # Commit and return response
    pass

@router.get("/profile/{user_id}")
async def get_profile(user: int =  Depends(oauth2.get_current_user)):
    # Return profile details, including posts and follower count
    pass

@router.patch("/profile/update/")
async def update_profile(profile: schemas.ProfileUpdate, current_user: int =  Depends(oauth2.get_current_user)):
    # Update location, relationship status, and bio in profile
    if profile.location:
        current_user.location = profile.location
    if profile.relationship_status:
        current_user.relationship_status = profile.relationship_status
    if profile.bio:
        current_user.bio = profile.bio
    # Commit changes
    pass


@router.post("/wall/")
async def create_wall_post(post: schemas.WallPostCreate, current_user: int =  Depends(oauth2.get_current_user)):
    # Add a new post to the user’s wall
    wall_post = models.WallPost(author_id=current_user.id, content=post.content)
    activity = models.Activity(user_id=current_user.id, action="posted on their wall")
    # Commit and return response
    pass

@router.get("/activity/{user_id}")
async def get_recent_activity(user_id: int):
    # Return recent activity feed for a user
    pass


@router.patch("/settings/privacy/")
async def update_privacy(is_private: bool, current_user: int =  Depends(oauth2.get_current_user)):
    # Update user's privacy setting
    current_user.is_private = is_private
    pass