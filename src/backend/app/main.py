from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from app.database import engine, Base
# Import models BEFORE creating tables so SQLAlchemy knows about them
from app import models
from app.routes import auth, users, posts, comments, social, notifications, messages
from app.routes import public_api, apikeys

# Validate required secrets at startup
_SECRET_KEY = os.getenv("SECRET_KEY")
_ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not _SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable must be set")
if not _ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY environment variable must be set")

# Create database tables
Base.metadata.create_all(bind=engine)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Transcendence Social Network API",
    description="Backend API for 42 Transcendence Social Network",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware — restrict to ALLOWED_ORIGINS env var (comma-separated), default to frontend
_raw_origins = os.getenv("ALLOWED_ORIGINS", "https://localhost:8080")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-New-Access-Token", "X-New-Refresh-Token"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(social.router)
app.include_router(notifications.router)
app.include_router(messages.router)
app.include_router(public_api.router)
app.include_router(apikeys.router)


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "Transcendence Social Network API is running"}


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Transcendence Social Network API",
        "docs": "/docs",
        "health": "/health"
    }