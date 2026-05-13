from datetime import timedelta
import logging
import os
import smtplib
import re
from email.mime.text import MIMEText
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt as jose_jwt, JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address
import httpx

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, LoginRequest, Token, RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    get_current_active_user,
    verify_password,
)

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        display_name=user_data.username
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token (form data for Swagger UI compatibility)"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Update user online status
    user.is_online = True
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout the current user"""
    current_user.is_online = False
    db.commit()
    return {"message": "Successfully logged out"}


@router.get("/verify", response_model=UserResponse)
async def verify_token_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """Verify the current token and return user info"""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    body: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Exchange a refresh token for a new access token"""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        from app.auth import SECRET_KEY
        payload = jose_jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_error
        username: str = payload.get("sub")
        if not username:
            raise credentials_error
    except Exception:
        raise credentials_error

    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        raise credentials_error

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": new_refresh_token}


def _send_reset_email(to_email: str, reset_url: str) -> None:
    """Send a password reset email via SMTP. Logs the URL if SMTP is not configured."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "noreply@transcendence.local")

    if not smtp_host or not smtp_user:
        logger.warning("SMTP not configured — password reset URL for %s: %s", to_email, reset_url)
        return

    msg = MIMEText(
        f"Click the link below to reset your password (valid 15 minutes):\n\n{reset_url}\n\n"
        f"If you did not request this, ignore this email."
    )
    msg["Subject"] = "Password reset"
    msg["From"] = smtp_from
    msg["To"] = to_email

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, [to_email], msg.as_string())
    except Exception as exc:
        logger.error("Failed to send reset email to %s: %s", to_email, exc)


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Request a password-reset link sent to the given email address.
    Always returns 202 to avoid email enumeration."""
    from app.auth import SECRET_KEY
    user = db.query(User).filter(User.email == body.email, User.is_active == True).first()
    if user:
        payload = {"sub": user.username, "type": "password_reset"}
        token = jose_jwt.encode(
            {**payload, "exp": __import__("datetime").datetime.utcnow() + timedelta(minutes=15)},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8080")
        reset_url = f"{frontend_url}/reset-password?token={token}"
        _send_reset_email(user.email, reset_url)
    return {"message": "If that email exists you will receive a reset link shortly."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Consume a password-reset token and set a new password."""
    from app.auth import SECRET_KEY
    invalid = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    try:
        payload = jose_jwt.decode(body.token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            raise invalid
        username: str = payload.get("sub")
        if not username:
            raise invalid
    except JWTError:
        raise invalid

    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        raise invalid

    user.hashed_password = get_password_hash(body.new_password)
    db.commit()
    return {"message": "Password updated successfully"}


# ── Google OAuth2 ─────────────────────────────────────────────────────────────

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def _google_redirect_uri(request: Request) -> str:
    """Build the absolute callback URI from the incoming request."""
    frontend_url = os.getenv("FRONTEND_URL", str(request.base_url).rstrip("/"))
    backend_base = str(request.base_url).rstrip("/")
    return f"{backend_base}/api/auth/google/callback"


@router.get("/google")
async def google_login(request: Request):
    """Redirect the user to Google's OAuth2 consent screen."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google OAuth is not configured")

    redirect_uri = _google_redirect_uri(request)
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/google/callback")
async def google_callback(code: str, request: Request, db: Session = Depends(get_db)):
    """Handle the OAuth2 callback from Google, find or create the user,
    and redirect the frontend with JWT tokens as query parameters."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=501, detail="Google OAuth is not configured")

    redirect_uri = _google_redirect_uri(request)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8080")

    # Exchange authorisation code for Google tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json"},
        )
        if token_resp.status_code != 200:
            logger.error("Google token exchange failed: %s", token_resp.text)
            return RedirectResponse(f"{frontend_url}/login?error=google_token_failed")

        google_tokens = token_resp.json()
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_tokens['access_token']}"},
        )
        if userinfo_resp.status_code != 200:
            logger.error("Google userinfo fetch failed: %s", userinfo_resp.text)
            return RedirectResponse(f"{frontend_url}/login?error=google_userinfo_failed")

        userinfo = userinfo_resp.json()

    google_id: str = userinfo["sub"]
    email: str = userinfo.get("email", "")
    name: str = userinfo.get("name", "")
    picture: str = userinfo.get("picture", "")

    # Find existing user by google_id or email
    user = db.query(User).filter(User.google_id == google_id).first()
    if not user and email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Link existing account to Google
            user.google_id = google_id
            if picture and not user.avatar_url:
                user.avatar_url = picture
            db.commit()

    if not user:
        # Create a new account — derive a unique username from the Google name/email
        base = re.sub(r"[^a-zA-Z0-9_]", "", (name or email.split("@")[0]))[:28] or "user"
        username = base
        suffix = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base}{suffix}"
            suffix += 1

        user = User(
            username=username,
            email=email,
            hashed_password=None,
            google_id=google_id,
            display_name=name or username,
            avatar_url=picture or None,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        return RedirectResponse(f"{frontend_url}/login?error=account_inactive")

    # Issue our own JWT tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    user.is_online = True
    db.commit()

    return RedirectResponse(
        f"{frontend_url}/oauth/callback"
        f"?access_token={access_token}"
        f"&refresh_token={refresh_token}"
        f"&token_type=bearer"
    )
