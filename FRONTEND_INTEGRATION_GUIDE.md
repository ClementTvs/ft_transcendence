# Frontend Integration Guide

## Quick Start for Frontend Developers

This guide explains how to connect the Vue.js frontend to our FastAPI backend.

---

## 🔧 Backend Setup

1. **Start the backend:**
   ```bash
   docker-compose up --build
   ```

2. **Backend is running at:**
   - API: `http://localhost:8000`
   - Interactive docs: `http://localhost:8000/docs` (use this to test endpoints!)
   - Frontend: `http://localhost` (port 80)

---

## 🔐 Authentication Flow (How Login Works)

### Step 1: Register a User
**POST** `/api/auth/register`

```javascript
// Request
const response = await fetch('http://localhost:8000/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: "john_doe",
    email: "john@example.com",
    password: "password123"
  })
});

const user = await response.json();
// Response: { id: 1, username: "john_doe", email: "john@example.com", ... }
```

### Step 2: Login
**POST** `/api/auth/login`

```javascript
// Request
const response = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: "john_doe",
    password: "password123"
  })
});

const data = await response.json();
// Response: { access_token: "eyJhbGciOi...", token_type: "bearer" }

// IMPORTANT: Save this token!
localStorage.setItem('access_token', data.access_token);
```

### Step 3: Use Token for Protected Endpoints
For any endpoint that requires authentication, add the token to headers:

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/users/me', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const currentUser = await response.json();
```

### Step 4: Logout
**POST** `/api/auth/logout`

```javascript
const token = localStorage.getItem('access_token');

await fetch('http://localhost:8000/api/auth/logout', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});

// Clear the token
localStorage.removeItem('access_token');
```

---

## 📝 Common Operations

### Creating a Post
**POST** `/api/posts/`

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/posts/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: "Hello world! This is my first post.",
    image_url: null  // optional
  })
});

const newPost = await response.json();
// Response: { id: 1, content: "Hello world!", author_id: 1, like_count: 0, ... }
```

### Getting the Feed
**GET** `/api/posts/`

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/posts/', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const posts = await response.json();
// Response: [{ id: 1, content: "...", author: { username: "..." }, ... }, ...]
```

### Liking a Post
**POST** `/api/posts/{post_id}/like`

```javascript
const token = localStorage.getItem('access_token');
const postId = 1;

await fetch(`http://localhost:8000/api/posts/${postId}/like`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
// Response: { message: "Post liked successfully" }
```

### Following a User
**POST** `/api/social/follow/{user_id}`

```javascript
const token = localStorage.getItem('access_token');
const userId = 5;

await fetch(`http://localhost:8000/api/social/follow/${userId}`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### Adding a Comment
**POST** `/api/comments/`

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/comments/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    post_id: 1,
    content: "Great post!"
  })
});

const comment = await response.json();
```

---

## 🎯 Recommended Frontend Structure

### 1. Create an API Service File

**`src/services/api.js`**
```javascript
const API_URL = 'http://localhost:8000';

// Get token from localStorage
const getToken = () => localStorage.getItem('access_token');

// Generic request function
async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
  };

  const response = await fetch(`${API_URL}${endpoint}`, config);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }
  
  return response.json();
}

// Auth API
export const authAPI = {
  register: (username, email, password) =>
    apiRequest('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    }),
  
  login: async (username, password) => {
    const data = await apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    localStorage.setItem('access_token', data.access_token);
    return data;
  },
  
  logout: async () => {
    await apiRequest('/api/auth/logout', { method: 'POST' });
    localStorage.removeItem('access_token');
  },
  
  getCurrentUser: () => apiRequest('/api/users/me'),
};

// Posts API
export const postsAPI = {
  getAll: () => apiRequest('/api/posts/'),
  getFollowing: () => apiRequest('/api/posts/following'),
  getById: (id) => apiRequest(`/api/posts/${id}`),
  create: (content, image_url = null) =>
    apiRequest('/api/posts/', {
      method: 'POST',
      body: JSON.stringify({ content, image_url }),
    }),
  like: (postId) => apiRequest(`/api/posts/${postId}/like`, { method: 'POST' }),
  unlike: (postId) => apiRequest(`/api/posts/${postId}/like`, { method: 'DELETE' }),
};

// Users API
export const usersAPI = {
  search: (query) => apiRequest(`/api/users/?search=${query}`),
  getById: (id) => apiRequest(`/api/users/${id}`),
  getStats: (id) => apiRequest(`/api/users/${id}/stats`),
  updateProfile: (updates) =>
    apiRequest('/api/users/me', {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),
};

// Social API
export const socialAPI = {
  follow: (userId) => apiRequest(`/api/social/follow/${userId}`, { method: 'POST' }),
  unfollow: (userId) => apiRequest(`/api/social/unfollow/${userId}`, { method: 'DELETE' }),
  getFollowers: (userId) => apiRequest(`/api/social/followers/${userId}`),
  getFollowing: (userId) => apiRequest(`/api/social/following/${userId}`),
  isFollowing: (userId) => apiRequest(`/api/social/is-following/${userId}`),
};

// Comments API
export const commentsAPI = {
  getForPost: (postId) => apiRequest(`/api/comments/post/${postId}`),
  create: (postId, content) =>
    apiRequest('/api/comments/', {
      method: 'POST',
      body: JSON.stringify({ post_id: postId, content }),
    }),
};
```

### 2. Use in Vue Components

**Example: Login Page (`src/view/Login.vue`)**
```vue
<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authAPI } from '@/services/api';

const router = useRouter();
const username = ref('');
const password = ref('');
const error = ref('');

async function handleLogin() {
  try {
    await authAPI.login(username.value, password.value);
    router.push('/'); // Redirect to home
  } catch (err) {
    error.value = err.message;
  }
}
</script>

<template>
  <div>
    <input v-model="username" placeholder="Username" />
    <input v-model="password" type="password" placeholder="Password" />
    <button @click="handleLogin">Login</button>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>
```

### 3. Use Pinia for User State

**`src/stores/user.js`**
```javascript
import { defineStore } from 'pinia';
import { authAPI } from '@/services/api';

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null,
    isAuthenticated: false,
  }),
  
  actions: {
    async loadCurrentUser() {
      try {
        this.currentUser = await authAPI.getCurrentUser();
        this.isAuthenticated = true;
      } catch (error) {
        this.currentUser = null;
        this.isAuthenticated = false;
      }
    },
    
    async login(username, password) {
      await authAPI.login(username, password);
      await this.loadCurrentUser();
    },
    
    async logout() {
      await authAPI.logout();
      this.currentUser = null;
      this.isAuthenticated = false;
    },
  },
});
```

---

## 📚 All Available Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (returns token)
- `POST /api/auth/logout` - Logout (requires auth)
- `GET /api/auth/verify` - Verify token (requires auth)

### Users
- `GET /api/users/me` - Get current user (requires auth)
- `PUT /api/users/me` - Update profile (requires auth)
- `DELETE /api/users/me` - Delete account (requires auth)
- `GET /api/users/{user_id}` - Get user by ID (requires auth)
- `GET /api/users/` - List users, supports `?search=query` (requires auth)
- `GET /api/users/{user_id}/stats` - Get user stats (requires auth)

### Posts
- `POST /api/posts/` - Create post (requires auth)
- `GET /api/posts/` - Get all posts (requires auth)
- `GET /api/posts/following` - Get posts from followed users (requires auth)
- `GET /api/posts/user/{user_id}` - Get user's posts (requires auth)
- `GET /api/posts/{post_id}` - Get single post (requires auth)
- `PUT /api/posts/{post_id}` - Update post (requires auth, author only)
- `DELETE /api/posts/{post_id}` - Delete post (requires auth, author only)
- `POST /api/posts/{post_id}/like` - Like post (requires auth)
- `DELETE /api/posts/{post_id}/like` - Unlike post (requires auth)

### Comments
- `POST /api/comments/` - Create comment (requires auth)
- `GET /api/comments/post/{post_id}` - Get post's comments (requires auth)
- `GET /api/comments/{comment_id}` - Get single comment (requires auth)
- `PUT /api/comments/{comment_id}` - Update comment (requires auth, author only)
- `DELETE /api/comments/{comment_id}` - Delete comment (requires auth, author only)

### Social
- `POST /api/social/follow/{user_id}` - Follow user (requires auth)
- `DELETE /api/social/unfollow/{user_id}` - Unfollow user (requires auth)
- `GET /api/social/followers/{user_id}` - Get user's followers (requires auth)
- `GET /api/social/following/{user_id}` - Get who user follows (requires auth)
- `GET /api/social/is-following/{user_id}` - Check if following (requires auth)
- `GET /api/social/suggestions` - Get follow suggestions (requires auth)

---

## 🐛 Common Issues & Solutions

### Issue: "CORS error"
**Solution:** Backend has CORS enabled for all origins. Make sure backend is running.

### Issue: "401 Unauthorized"
**Solution:** Token expired or missing. Check if token is in localStorage and being sent in headers.

### Issue: "Token not found in localStorage"
**Solution:** User needs to login first. Redirect to `/login`.

### Issue: "Cannot read property of undefined"
**Solution:** API returned an error. Always check `response.ok` before using data.

---

## 💡 Quick Testing (No Frontend Needed)

Use the **interactive API docs** at `http://localhost:8000/docs`:

1. Click on any endpoint (e.g., `POST /api/auth/register`)
2. Click "Try it out"
3. Fill in the request body
4. Click "Execute"
5. See the response

This is the **easiest way** to understand what the backend expects and returns!

---

## 🎨 Frontend TODO Checklist

- [ ] Create `src/services/api.js` with API functions
- [ ] Update `src/stores/user.js` for authentication state
- [ ] Implement Login page functionality
- [ ] Implement Register page functionality
- [ ] Create Home page with post feed
- [ ] Create Post creation component
- [ ] Create Profile page
- [ ] Add route guards (redirect to login if not authenticated)
- [ ] Add loading states
- [ ] Add error handling

---

## 📞 Need Help?

1. **Test in browser**: Go to `http://localhost:8000/docs`
2. **Check backend logs**: See docker-compose terminal output
3. **Check browser console**: Look for error messages
4. **Verify token**: `console.log(localStorage.getItem('access_token'))`

Good luck! 🚀
