from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
import shutil

from app.database import get_db
from app.models import User, Post, Follow
from app.schemas import UserResponse, UserUpdate, UserWithStats, PasswordChange
from app.auth import get_current_active_user, get_password_hash, verify_password

router = APIRouter(prefix="/api/users", tags=["users"])

UPLOAD_DIR = "static"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get the current user's profile"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db)
):
    """Get a list of users (with optional search)"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.display_name.ilike(f"%{search}%"))
        )
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update the current user's profile"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Check if email is being changed and if it's already taken
    if "email" in update_data:
        existing_user = db.query(User).filter(User.email == update_data["email"]).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete the current user's account (soft delete)"""
    current_user.is_active = False
    db.commit()
    return None


@router.get("/{user_id}/stats", response_model=UserWithStats)
async def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a user's social statistics"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Count posts
    post_count = db.query(Post).filter(Post.author_id == user_id).count()
    
    # Count followers
    follower_count = db.query(Follow).filter(Follow.followed_id == user_id).count()
    
    # Count following
    following_count = db.query(Follow).filter(Follow.follower_id == user_id).count()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "banner_url": user.banner_url,
        "is_active": user.is_active,
        "is_online": user.is_online,
        "created_at": user.created_at,
        "post_count": post_count,
        "follower_count": follower_count,
        "following_count": following_count
    }


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Le fichier doit être une image (jpeg, png, gif, webp)")

    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"avatar_{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    current_user.avatar_url = f"/static/{filename}"
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/banner", response_model=UserResponse)
async def upload_banner(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Le fichier doit être une image (jpeg, png, gif, webp)")

    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"banner_{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    current_user.banner_url = f"/static/{filename}"
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/password", status_code=status.HTTP_200_OK)
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change the current user's password"""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
