from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.database import get_db
from app.models import User, Post, Like, Comment, Notification
from app.schemas import PostCreate, PostUpdate, PostResponse, PostWithAuthor, UserResponse
from app.auth import get_current_active_user
from app.ws_manager import notif_manager

router = APIRouter(prefix="/api/posts", tags=["posts"])


def get_post_with_counts(post: Post, current_user_id: int = None):
    """Helper function to add like/comment counts and is_liked flag"""
    post_dict = {
        "id": post.id,
        "content": post.content,
        "image_url": post.image_url,
        "author_id": post.author_id,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "like_count": len(post.likes),
        "comment_count": len(post.comments),
        "is_liked": False
    }
    
    if current_user_id:
        post_dict["is_liked"] = any(like.user_id == current_user_id for like in post.likes)
    
    return post_dict


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    new_post = Post(
        content=post_data.content,
        image_url=post_data.image_url,
        author_id=current_user.id
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return get_post_with_counts(new_post, current_user.id)


@router.get("/", response_model=List[PostWithAuthor])
async def get_posts(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all posts (feed) ordered by newest first"""
    posts = db.query(Post).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for post in posts:
        post_dict = get_post_with_counts(post, current_user.id)
        post_dict["author"] = post.author
        result.append(post_dict)
    
    return result


@router.get("/following", response_model=List[PostWithAuthor])
async def get_following_posts(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get posts from users that the current user follows"""
    # Get IDs of users that current user follows
    from app.models import Follow
    following_ids = [f.followed_id for f in current_user.following]
    
    if not following_ids:
        return []
    
    posts = db.query(Post).filter(
        Post.author_id.in_(following_ids)
    ).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for post in posts:
        post_dict = get_post_with_counts(post, current_user.id)
        post_dict["author"] = post.author
        result.append(post_dict)
    
    return result


@router.get("/user/{user_id}", response_model=List[PostWithAuthor])
async def get_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all posts by a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    posts = db.query(Post).filter(
        Post.author_id == user_id
    ).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for post in posts:
        post_dict = get_post_with_counts(post, current_user.id)
        post_dict["author"] = post.author
        result.append(post_dict)
    
    return result


@router.get("/{post_id}", response_model=PostWithAuthor)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific post by ID"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_dict = get_post_with_counts(post, current_user.id)
    post_dict["author"] = post.author
    
    return post_dict


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a post (only by the author)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own posts"
        )
    
    update_data = post_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    
    return get_post_with_counts(post, current_user.id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a post (only by the author)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own posts"
        )
    
    db.delete(post)
    db.commit()
    
    return None


@router.get("/{post_id}/likes", response_model=List[UserResponse])
async def get_post_likes(
    post_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get the list of users who liked a specific post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return [like.user for like in post.likes[skip: skip + limit]]


@router.post("/{post_id}/like", status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Like a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if already liked
    existing_like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already liked"
        )
    
    new_like = Like(post_id=post_id, user_id=current_user.id)
    db.add(new_like)
    db.commit()

    if post.author_id != current_user.id:
        new_notification = Notification(
            user_id=post.author_id,
            post_id=post.id,
            actor_id=current_user.id,
            type="like"
        )
        db.add(new_notification)
        db.commit()
        await notif_manager.send_to_user(post.author_id, {
            "type": "like",
            "actor_id": current_user.id,
            "actor_username": current_user.username,
            "post_id": post.id,
        })
    
    return {"message": "Post liked successfully"}


@router.delete("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlike a post"""
    like = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user.id
    ).first()
    
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(like)
    db.commit()
    
    return None
