# Transcendence Backend API

A FastAPI-based backend for the 42 Transcendence project (Social Network).

## Features

- ✅ User authentication with JWT tokens
- ✅ User registration and profile management
- ✅ Post creation, editing, and deletion
- ✅ Comments on posts
- ✅ Like/unlike posts
- ✅ Follow/unfollow users
- ✅ User feed (all posts and following feed)
- ✅ User statistics (posts, followers, following)
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ CORS enabled for frontend integration

## API Endpoints

### Authentication (`/api/auth`)

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token
- `POST /api/auth/logout` - Logout current user
- `GET /api/auth/verify` - Verify token and get user info

### Users (`/api/users`)

- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update current user profile
- `DELETE /api/users/me` - Deactivate current user account
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/` - Get list of users (supports search query)
- `GET /api/users/{user_id}/stats` - Get user social statistics

### Posts (`/api/posts`)

- `POST /api/posts/` - Create a new post
- `GET /api/posts/` - Get all posts (feed, newest first)
- `GET /api/posts/following` - Get posts from users you follow
- `GET /api/posts/user/{user_id}` - Get all posts by a specific user
- `GET /api/posts/{post_id}` - Get a specific post
- `PUT /api/posts/{post_id}` - Update a post (author only)
- `DELETE /api/posts/{post_id}` - Delete a post (author only)
- `POST /api/posts/{post_id}/like` - Like a post
- `DELETE /api/posts/{post_id}/like` - Unlike a post

### Comments (`/api/comments`)

- `POST /api/comments/` - Create a new comment on a post
- `GET /api/comments/post/{post_id}` - Get all comments for a post
- `GET /api/comments/{comment_id}` - Get a specific comment
- `PUT /api/comments/{comment_id}` - Update a comment (author only)
- `DELETE /api/comments/{comment_id}` - Delete a comment (author only)

### Social (`/api/social`)

- `POST /api/social/follow/{user_id}` - Follow a user
- `DELETE /api/social/unfollow/{user_id}` - Unfollow a user
- `GET /api/social/followers/{user_id}` - Get all followers of a user
- `GET /api/social/following/{user_id}` - Get all users that a user follows
- `GET /api/social/is-following/{user_id}` - Check if you're following a user
- `GET /api/social/suggestions` - Get suggested users to follow

### Health

- `GET /health` - Health check endpoint
- `GET /` - API information

## Database Models

### User
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `display_name`: Display name
- `bio`: User biography
- `avatar_url`: Profile picture URL
- `is_active`: Account active status
- `is_online`: Current online status
- `created_at`, `updated_at`: Timestamps
- Relationships: `posts`, `comments`, `likes`, `following`, `followers`

### Post
- `id`: Primary key
- `content`: Post text content
- `image_url`: Optional image URL
- `author_id`: Foreign key to User
- `created_at`, `updated_at`: Timestamps
- Relationships: `author`, `comments`, `likes`

### Comment
- `id`: Primary key
- `content`: Comment text
- `post_id`: Foreign key to Post
- `author_id`: Foreign key to User
- `created_at`, `updated_at`: Timestamps
- Relationships: `post`, `author`

### Like
- `id`: Primary key
- `post_id`: Foreign key to Post
- `user_id`: Foreign key to User
- `created_at`: Timestamp
- Relationships: `post`, `user`

### Follow
- `id`: Primary key
- `follower_id`: User who is following
- `followed_id`: User being followed
- `created_at`: Timestamp
- Relationships: `follower`, `followed`

## Development

### Run locally with Docker Compose

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

- `POSTGRES_USER`: Database user (default: postgres)
- `POSTGRES_PASSWORD`: Database password (default: postgres)
- `POSTGRES_DB`: Database name (default: transcendence)
- `POSTGRES_HOST`: Database host (default: db)
- `POSTGRES_PORT`: Database port (default: 5432)
- `SECRET_KEY`: JWT secret key (change in production!)

## Authentication

The API uses JWT Bearer tokens for authentication. After login, include the token in requests:

```
Authorization: Bearer <your-token>
```

## Features Implemented

### Core Social Features
✅ User profiles with bio and avatar  
✅ Create, read, update, delete posts  
✅ Post with optional images  
✅ Comment on posts  
✅ Like/unlike posts  
✅ Follow/unfollow users  
✅ View follower/following lists  

### Feed Features
✅ Global feed (all posts)  
✅ Following feed (posts from followed users)  
✅ User profile feed (posts by specific user)  
✅ Posts show like count and comment count  
✅ Posts show if current user has liked them  

### User Features
✅ Search users by username or display name  
✅ User statistics (post count, followers, following)  
✅ Follow suggestions (users not currently following)  
✅ Profile editing (bio, display name, avatar)  

## Next Steps

- [ ] Add image upload functionality
- [ ] Add real-time notifications
- [ ] Add direct messaging
- [ ] Add hashtag support
- [ ] Add post search functionality
- [ ] Add user blocking
- [ ] Add content moderation
- [ ] Add analytics/insights
- [ ] Add OAuth integration (42 API, GitHub, Google)
- [ ] Add password reset functionality
