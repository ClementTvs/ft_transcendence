from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.database import get_db, SessionLocal
from app.models import User, Conversation, Message
from app.schemas import MessageResponse, ConversationResponse
from app.auth import get_current_active_user, verify_token
from app.ws_manager import manager
from app.crypto import encrpypt_message, decrypt_message

router = APIRouter(prefix="/api/messages", tags=["messages"])


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _build_message(msg: Message) -> dict:
    return {
        "id": msg.id,
        "conversation_id": msg.conversation_id,
        "sender_id": msg.sender_id,
        "content": decrypt_message(msg.content),
        "created_at": msg.created_at,
        "is_read": msg.is_read,
        "sender": msg.sender,
    }


def _build_conversation(conv: Conversation, current_user_id: int, db: Session) -> dict:
    other = conv.user2 if conv.user1_id == current_user_id else conv.user1

    last_msg = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.created_at.desc())
        .first()
    )

    unread_count = (
        db.query(Message)
        .filter(
            Message.conversation_id == conv.id,
            Message.sender_id != current_user_id,
            Message.is_read == False,
        )
        .count()
    )

    return {
        "id": conv.id,
        "user1_id": conv.user1_id,
        "user2_id": conv.user2_id,
        "created_at": datetime.now(timezone.utc),
        "other_user": other,
        "last_message": _build_message(last_msg) if last_msg else None,
        "unread_count": unread_count,
    }


# ─── REST Routes ──────────────────────────────────────────────────────────────

@router.post("/conversations/{user_id}", response_model=ConversationResponse)
def get_or_create_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot start a conversation with yourself")

    other_user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")

    conv = (
        db.query(Conversation)
        .filter(
            or_(
                and_(Conversation.user1_id == current_user.id, Conversation.user2_id == user_id),
                and_(Conversation.user1_id == user_id, Conversation.user2_id == current_user.id),
            )
        )
        .first()
    )

    if not conv:
        conv = Conversation(user1_id=current_user.id, user2_id=user_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)

    return _build_conversation(conv, current_user.id, db)


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    conversations = (
        db.query(Conversation)
        .filter(
            or_(
                Conversation.user1_id == current_user.id,
                Conversation.user2_id == current_user.id,
            )
        )
        .all()
    )
    return [_build_conversation(c, current_user.id, db) for c in conversations]


@router.get("/conversations/{conv_id}/messages", response_model=List[MessageResponse])
def get_messages(
    conv_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if current_user.id not in (conv.user1_id, conv.user2_id):
        raise HTTPException(status_code=403, detail="Access denied")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_build_message(m) for m in messages]


@router.put("/conversations/{conv_id}/read")
def mark_as_read(
    conv_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if current_user.id not in (conv.user1_id, conv.user2_id):
        raise HTTPException(status_code=403, detail="Access denied")

    db.query(Message).filter(
        Message.conversation_id == conv_id,
        Message.sender_id != current_user.id,
        Message.is_read == False,
    ).update({"is_read": True})
    db.commit()

    return {"detail": "Messages marked as read"}


# ─── WebSocket ────────────────────────────────────────────────────────────────

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, token: str = Query(...)):
    # Authenticate via query param (HTTP headers not available in WS handshake)
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

    if not user:
        db.close()
        await websocket.close(code=1008)
        return

    await manager.connect(user.id, websocket)
    user.is_online = True
    db.commit()

    try:
        while True:
            data = await websocket.receive_json()

            to_user_id = data.get("to_user_id")
            conv_id = data.get("conversation_id")
            content = data.get("content", "").strip()

            if not to_user_id or not conv_id or not content:
                continue

            # Verify the conversation belongs to this user
            conv = db.query(Conversation).filter(
                Conversation.id == conv_id,
                or_(
                    Conversation.user1_id == user.id,
                    Conversation.user2_id == user.id,
                ),
            ).first()
            if not conv:
                continue

            # Encrypt and persist
            new_msg = Message(
                conversation_id=conv_id,
                sender_id=user.id,
                content=encrpypt_message(content),
            )
            db.add(new_msg)
            db.commit()
            db.refresh(new_msg)

            # Send plain text to both clients (never the encrypted version)
            payload = {
                "id": new_msg.id,
                "conversation_id": conv_id,
                "sender_id": user.id,
                "content": content,
                "created_at": new_msg.created_at.isoformat() if new_msg.created_at else datetime.utcnow().isoformat(),
                "is_read": False,
            }

            await manager.send_to_user(to_user_id, payload)
            await manager.send_to_user(user.id, payload)

    except WebSocketDisconnect:
        pass

    finally:
        manager.disconnect(user.id)
        user.is_online = False
        db.commit()
        db.close()
