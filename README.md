*This project has been created as part of the 42 curriculum by alribeyr, gvalogne, ctravers, artperez.*

# ft_transcendence — Social Network & Gaming Platform

## Description

**ft_transcendence** is a full-stack social network web application built as a final project of the 42 school core curriculum. The platform lets users create an account, publish posts, follow other users, exchange real-time messages, and receive live notifications — all within a responsive, modern interface.

### Key Features

- **User accounts** — registration, login, profile editing (username, email, bio, avatar, banner)
- **Posts & feed** — create posts (with optional game tag via the RAWG public API and image upload), like, comment
- **Social graph** — follow / unfollow users, block / unblock, explore suggestions
- **Real-time chat** — private messaging with read receipts, powered by WebSockets
- **Live notifications** — follow, like, comment, and new-message events delivered instantly via WebSocket
- **Password reset** — email-based secure reset flow (JWT token, 15-minute expiry)
- **Privacy & Terms pages** — accessible from every page's footer
- **Dark / Light theme** — user preference persisted in localStorage
- **Fully containerised** — single `docker compose up` command to run the entire stack

---

## Team Information

| Login | Role | Responsibilities |
|---|---|---|
| alribeyr | TBD | TBD |
| gvalogne | TBD | TBD |
| ctravers | TBD | TBD |
| artperez | TBD | TBD |

---

## Project Management

- **Task distribution** — work was broken down into features and assigned per team member.
- **Project management tool** — Trello (kanban board with To Do / In Progress / Done columns).
- **Communication** — Discord (dedicated server).

---

## Technical Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Vue 3 | latest | SPA framework (Composition API) |
| Vue Router | 4 | Client-side routing |
| Pinia | latest | Global state management |
| Tailwind CSS | 3 | Utility-first styling |
| Vite | latest | Build tool and dev server |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python / FastAPI | 3.12 / latest | REST API + WebSocket server |
| SQLAlchemy | 2 | ORM — database access layer |
| Pydantic v2 | latest | Request/response validation |
| python-jose | latest | JWT generation and verification |
| passlib / bcrypt | latest | Password hashing |
| slowapi | latest | Rate limiting |

### Database
| Technology | Reason |
|---|---|
| PostgreSQL 16 | Mature relational DB with strong FK/cascade support; ideal for the relational data model (users → posts → comments → likes → follows). |

### Infrastructure
| Technology | Purpose |
|---|---|
| Docker + Docker Compose | Single-command deployment, isolated services |
| nginx (Alpine) | TLS termination, reverse proxy, SPA serving, WebSocket upgrade |
| OpenSSL (self-signed) | HTTPS with SAN for localhost (required by Chrome) |

### Justification for major choices
- **FastAPI** was chosen for its native async support (critical for WebSockets), automatic OpenAPI docs, and Pydantic integration.
- **Vue 3 (Composition API)** was chosen for its reactivity model, lightweight bundle, and easy integration with Pinia.
- **Tailwind CSS** avoids writing custom CSS, enabling rapid consistent UI without naming collisions.
- **PostgreSQL** over SQLite because the project requires concurrent multi-user writes; PostgreSQL handles locking and transactions safely at scale.

---

## Database Schema

Nine tables with the following relationships:

```
users ──< posts ──< comments
      │         └──< likes
      ├──< follows (self-ref: follower_id → users, followed_id → users)
      ├──< blocks  (self-ref: blocker_id → users, blocked_id → users)
      ├──< notifications (user_id → users, actor_id → users, post_id → posts)
      ├──< conversations (user1_id → users, user2_id → users)
      │         └──< messages (sender_id → users)
      └── (author of comments, likes, messages)
```

| Table | Key fields |
|---|---|
| `users` | `id`, `username` (UK), `email` (UK), `hashed_password`, `display_name`, `bio`, `avatar_url`, `banner_url`, `is_active`, `is_online` |
| `posts` | `id`, `content`, `image_url`, `author_id` FK |
| `comments` | `id`, `content`, `post_id` FK, `author_id` FK |
| `likes` | `id`, `post_id` FK, `user_id` FK |
| `follows` | `id`, `follower_id` FK, `followed_id` FK |
| `blocks` | `id`, `blocker_id` FK, `blocked_id` FK |
| `conversations` | `id`, `user1_id` FK, `user2_id` FK |
| `messages` | `id`, `conversation_id` FK, `sender_id` FK, `content` (encrypted), `is_read` |
| `notifications` | `id`, `user_id` FK, `actor_id` FK, `post_id` FK (nullable), `type`, `is_read` |

All user-owned data cascades on delete.

---

## Instructions

### Prerequisites

| Tool | Minimum version |
|---|---|
| Docker | 24+ |
| Docker Compose | v2 (`docker compose`) |
| Git | any |

> No other software needs to be installed on the host — everything runs in containers.

### 1. Clone the repository

```bash
git clone <repo-url>
cd transcengit
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

| Variable | What to set |
|---|---|
| `POSTGRES_PASSWORD` | any strong password |
| `SECRET_KEY` | long random string (e.g. `openssl rand -hex 32`) |
| `ENCRYPTION_KEY` | long random string (e.g. `openssl rand -hex 32`) |
| `ALLOWED_ORIGINS` | `https://localhost:8080` (default, change for production) |
| `FRONTEND_URL` | `https://localhost:8080` (default) |
| `SMTP_*` | optional — password-reset links are logged to console if unset |

### 3. Build and run

```bash
docker compose up --build
```

The first build downloads images and compiles the frontend (~2 minutes).

### 4. Open in browser

```
https://localhost:8080
```

Chrome will warn about the self-signed certificate. Click **Advanced → Proceed to localhost (unsafe)** once. This is required to allow `wss://` WebSocket connections.

### 5. Stop

```bash
docker compose down
```

Add `-v` to also delete all data volumes (database + uploaded images):

```bash
docker compose down -v
```

### Useful commands

```bash
# Rebuild after code changes
docker compose up --build

# View backend logs
docker compose logs -f backend

# Force full rebuild (no Docker layer cache)
docker compose build --no-cache && docker compose up
```

---

## Features List

| Feature | Description | Team member(s) |
|---|---|---|
| User registration & login | Email + password auth, bcrypt-hashed passwords, JWT tokens | TBD |
| Profile management | Edit username, email, bio, avatar, banner | TBD |
| Password reset | Email-based reset with expiring JWT token | TBD |
| Posts | Create (with image + game tag), edit, delete, view feed | TBD |
| Likes & comments | Like/unlike posts, comment thread per post | TBD |
| Follow / unfollow | Follow users, view followers/following lists | TBD |
| Block / unblock | Block users, removes follow relationship both ways | TBD |
| User search | Search by username or display name from the navbar | TBD |
| Explore page | Discover posts and users | TBD |
| Real-time chat | 1-on-1 private messages via WebSocket, read receipts | TBD |
| Live notifications | Follow, like, comment, message events via WebSocket | TBD |
| Game tagging | Attach a game to a post via RAWG public API search | TBD |
| Image uploads | Avatar, banner, and post images stored on disk | TBD |
| Dark / light theme | Toggle persisted in localStorage | TBD |
| Privacy Policy & Terms | Accessible pages with real content, linked in footer | TBD |
| Account deletion | Hard delete with full cascade cleanup | TBD |
| Additional browser support | Chrome + Firefox compatibility | TBD |

---

## Modules

> Major module = 2 pts · Minor module = 1 pt

| Module | Type | Points | Description | Implemented by |
|---|---|---|---|---|
| Frontend framework (Vue.js) | Major | 2 | Full SPA using Vue 3 + Vite + Pinia | TBD |
| Backend framework (FastAPI) | Major | 2 | REST + WebSocket API with FastAPI | TBD |
| Database ORM (SQLAlchemy) | Minor | 1 | All DB access via SQLAlchemy ORM | TBD |
| User management | Major | 2 | Registration, login, profile, avatar | TBD |
| WebSockets (chat + notifications) | Major | 2 | Real-time messaging and notification delivery | TBD |
| User interactions (follow/block) | Minor | 1 | Follow, unfollow, block, unblock | TBD |
| Live notifications | Minor | 1 | Real-time in-app notification system | TBD |
| Public API integration (RAWG) | Minor | 1 | Game search and tagging on posts | TBD |
| File management | Minor | 1 | Image upload (avatar, banner, post images) | TBD |
| Additional browser support | Minor | 1 | Chrome + Firefox compatibility | TBD |
| Advanced chat features | Major | 2 | Read receipts, conversation list, real-time updates | TBD |

## Individual Contributions

### alribeyr
- TBD
- Challenges: TBD

### gvalogne
- TBD
- Challenges: TBD

### ctravers
- TBD
- Challenges: TBD

### artperez
- TBD
- Challenges: TBD

---

## Resources

### Documentation
- [FastAPI official docs](https://fastapi.tiangolo.com/)
- [Vue 3 official docs](https://vuejs.org/)
- [SQLAlchemy 2.0 docs](https://docs.sqlalchemy.org/en/20/)
- [Pinia docs](https://pinia.vuejs.org/)
- [Tailwind CSS docs](https://tailwindcss.com/docs)
- [Docker Compose reference](https://docs.docker.com/compose/)
- [RAWG Video Games Database API](https://rawg.io/apidocs)
- [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [RFC 7519 — JSON Web Tokens](https://datatracker.ietf.org/doc/html/rfc7519)

### AI Usage

GitHub Copilot (Claude Sonnet) was used throughout the project for the following tasks:

- **Backend architecture** — generating boilerplate for FastAPI routers, SQLAlchemy models, and Pydantic schemas
- **WebSocket implementation** — designing the `ConnectionManager` and real-time notification/chat flows
- **Bug fixing** — diagnosing issues such as missing `subjectAltName` in the TLS cert (causing Chrome WebSocket failures), stale WS connection crashes, and cascade delete FK violations
- **Security review** — checking auth flows (JWT signing, bcrypt hashing, rate limiting)
- **Frontend components** — scaffolding Vue components and Pinia stores
- **Code explanations** — understanding library internals (SQLAlchemy cascades, FastAPI dependency injection)

All AI-generated code was reviewed, understood, and adapted by team members before being committed.

---

## Known Limitations

- Self-signed TLS certificate requires manual browser exception on first visit.
- Password reset emails require external SMTP configuration; without it the reset URL is only available in backend logs.
- Images are stored inside a Docker volume — no CDN or external object storage.