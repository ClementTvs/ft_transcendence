from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.database import get_db
from app.models import User, Post, Comment, Notification
from app.schemas import CommentCreate, CommentUpdate, CommentResponse, CommentWithAuthor
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new comment on a post"""
    # Verify post exists
    post = db.query(Post).filter(Post.id == comment_data.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    new_comment = Comment(
        content=comment_data.content,
        post_id=comment_data.post_id,
        author_id=current_user.id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    if post.author_id != current_user.id:
        new_notification = Notification(
            user_id=post.author_id,
            post_id=post.id,
            actor_id=current_user.id,
            type="comment"
        )
        db.add(new_notification)
        db.commit()
    
    return new_comment


@router.get("/post/{post_id}", response_model=List[CommentWithAuthor])
async def get_post_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all comments for a specific post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comments = db.query(Comment).filter(
        Comment.post_id == post_id
    ).order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()
    
    # Add author information
    result = []
    for comment in comments:
        comment_dict = {
            "id": comment.id,
            "content": comment.content,
            "post_id": comment.post_id,
            "author_id": comment.author_id,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "author": comment.author
        }
        result.append(comment_dict)
    
    return result


@router.get("/{comment_id}", response_model=CommentWithAuthor)
async def get_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific comment by ID"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return {
        "id": comment.id,
        "content": comment.content,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at,
        "author": comment.author
    }


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a comment (only by the author)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments"
        )
    
    comment.content = comment_update.content
    db.commit()
    db.refresh(comment)
    
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (only by the author)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments"
        )
    
    db.delete(comment)
    db.commit()
    
    return None
