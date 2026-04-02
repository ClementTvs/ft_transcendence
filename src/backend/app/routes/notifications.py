from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, SessionLocal
from app.models import User, Notification
from app.schemas import NotificationWithActor
from app.auth import get_current_active_user, verify_token
from app.ws_manager import notif_manager

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationWithActor])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all notifications for the current user, newest first"""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for notif in notifications:
        result.append({
            "id": notif.id,
            "user_id": notif.user_id,
            "post_id": notif.post_id,
            "actor_id": notif.actor_id,
            "type": notif.type,
            "created_at": notif.created_at,
            "is_read": notif.is_read,
            "actor": notif.actor
        })

    return result


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the number of unread notifications"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    return {"unread_count": count}


@router.put("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()

    return {"message": "All notifications marked as read"}


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a single notification as read"""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.commit()

    return {"message": "Notification marked as read"}


@router.websocket("/ws")
async def websocket_notifications(websocket: WebSocket, token: str = Query(...)):
    try:
        token_data = verify_token(token)
    except Exception:
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    user = db.query(User).filter(
        User.username == token_data.username,
        User.is_active == True,
    ).first()
    db.close()

    if not user:
        await websocket.close(code=1008)
        return

    await notif_manager.connect(user.id, websocket)

    try:
        while True:
            await websocket.receive_text()  # maintient la connexion, attrape le disconnect
    except WebSocketDisconnect:
        pass
    finally:
        notif_manager.disconnect(user.id)
