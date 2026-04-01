from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Follow, Notification
from app.schemas import FollowResponse, FollowWithUser, UserResponse
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/social", tags=["social"])


@router.post("/follow/{user_id}", status_code=status.HTTP_201_CREATED)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Follow a user"""
    # Check if user exists
    user_to_follow = db.query(User).filter(User.id == user_id).first()
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Can't follow yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself"
        )
    
    # Check if already following
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followed_id == user_id
    ).first()
    
    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already following this user"
        )
    
    new_follow = Follow(
        follower_id=current_user.id,
        followed_id=user_id
    )
    
    db.add(new_follow)
    db.commit()
    new_notification = Notification(
        user_id=user_to_follow.id,
        actor_id=current_user.id,
        type="follow"
    )
    db.add(new_notification)
    db.commit()
    
    return {"message": f"Successfully followed user {user_to_follow.username}"}


@router.delete("/unfollow/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user"""
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followed_id == user_id
    ).first()
    
    if not follow:
        raise HTTPException(
            status_code=404,
            detail="You are not following this user"
        )
    
    db.delete(follow)
    db.commit()
    
    return None


@router.get("/followers/{user_id}", response_model=List[FollowWithUser])
async def get_followers(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all followers of a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    followers = db.query(Follow).filter(
        Follow.followed_id == user_id
    ).offset(skip).limit(limit).all()
    
    result = []
    for follow in followers:
        result.append({
            "id": follow.id,
            "user": follow.follower,
            "created_at": follow.created_at
        })
    
    return result


@router.get("/following/{user_id}", response_model=List[FollowWithUser])
async def get_following(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all users that a user is following"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    following = db.query(Follow).filter(
        Follow.follower_id == user_id
    ).offset(skip).limit(limit).all()
    
    result = []
    for follow in following:
        result.append({
            "id": follow.id,
            "user": follow.followed,
            "created_at": follow.created_at
        })
    
    return result


@router.get("/is-following/{user_id}")
async def check_following(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if current user is following a specific user"""
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followed_id == user_id
    ).first()
    
    return {"is_following": follow is not None}


@router.get("/suggestions", response_model=List[UserResponse])
async def get_follow_suggestions(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get suggested users to follow (users not currently following)"""
    # Get IDs of users already following
    following_ids = [f.followed_id for f in current_user.following]
    following_ids.append(current_user.id)  # Exclude self
    
    # Get users not in the following list
    suggestions = db.query(User).filter(
        User.id.notin_(following_ids),
        User.is_active == True
    ).limit(limit).all()
    
    return suggestions
