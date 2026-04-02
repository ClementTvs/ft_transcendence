from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
# Import models BEFORE creating tables so SQLAlchemy knows about them
from app import models
from app.routes import auth, users, posts, comments, social, notifications, messages

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Transcendence Social Network API",
    description="Backend API for 42 Transcendence Social Network",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(social.router)
app.include_router(notifications.router)
app.include_router(messages.router)


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