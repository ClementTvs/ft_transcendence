"""
Public REST API — authenticated via X-API-Key header.
Rate limit: 60 requests / minute per IP.

Endpoints
---------
GET    /public/api/users              List users (paginated, optional ?search=)
GET    /public/api/users/{user_id}    Get a single user
GET    /public/api/posts              List posts (paginated, optional ?author_id=)
POST   /public/api/posts              Create a post
PUT    /public/api/posts/{post_id}    Update your own post
DELETE /public/api/posts/{post_id}    Delete your own post
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models import APIKey, User, Post

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/public/api", tags=["Public API"])


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

def get_api_user(
    x_api_key: str = Header(..., description="Your personal API key (sk_…)"),
    db: Session = Depends(get_db),
) -> User:
    """Resolve an X-API-Key header to the owning User."""
    record = (
        db.query(APIKey)
        .filter(APIKey.key == x_api_key, APIKey.is_active == True)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
        )
    if not record.user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    return record.user


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PublicUserOut(BaseModel):
    id: int
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    is_online: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PublicPostOut(BaseModel):
    id: int
    content: str
    image_url: Optional[str]
    author_id: int
    author_username: str
    like_count: int
    comment_count: int
    created_at: datetime


class PostCreateIn(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    image_url: Optional[str] = None


class PostUpdateIn(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=2000)
    image_url: Optional[str] = None


def _serialize_post(post: Post) -> dict:
    return {
        "id": post.id,
        "content": post.content,
        "image_url": post.image_url,
        "author_id": post.author_id,
        "author_username": post.author.username if post.author else "",
        "like_count": len(post.likes),
        "comment_count": len(post.comments),
        "created_at": post.created_at,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/users", response_model=List[PublicUserOut], summary="List users")
@limiter.limit("60/minute")
def list_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Filter by username"),
    db: Session = Depends(get_db),
    _user: User = Depends(get_api_user),
):
    """Returns a paginated list of active users."""
    q = db.query(User).filter(User.is_active == True)
    if search:
        q = q.filter(User.username.ilike(f"%{search}%"))
    return q.order_by(User.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/users/{user_id}", response_model=PublicUserOut, summary="Get a user")
@limiter.limit("60/minute")
def get_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_api_user),
):
    """Returns a single user by ID."""
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/posts", summary="List posts")
@limiter.limit("60/minute")
def list_posts(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    db: Session = Depends(get_db),
    _user: User = Depends(get_api_user),
):
    """Returns a paginated list of posts, newest first."""
    q = db.query(Post)
    if author_id is not None:
        q = q.filter(Post.author_id == author_id)
    posts = q.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return [_serialize_post(p) for p in posts]


@router.post("/posts", status_code=status.HTTP_201_CREATED, summary="Create a post")
@limiter.limit("60/minute")
def create_post(
    request: Request,
    body: PostCreateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_user),
):
    """Creates a new post on behalf of the API key owner."""
    post = Post(content=body.content, image_url=body.image_url, author_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return _serialize_post(post)


@router.put("/posts/{post_id}", summary="Update a post")
@limiter.limit("60/minute")
def update_post(
    request: Request,
    post_id: int,
    body: PostUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_user),
):
    """Updates a post. Only the post owner may update it."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own posts")
    if body.content is not None:
        post.content = body.content
    if body.image_url is not None:
        post.image_url = body.image_url
    db.commit()
    db.refresh(post)
    return _serialize_post(post)


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a post")
@limiter.limit("60/minute")
def delete_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_api_user),
):
    """Deletes a post. Only the post owner may delete it."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    db.delete(post)
    db.commit()
