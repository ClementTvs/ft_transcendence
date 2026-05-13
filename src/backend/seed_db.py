#!/usr/bin/env python3
"""
Script to seed the database with test data for Transcendence project.
Generates users, posts, comments, likes, follows and blocks.
"""

# Test logins / passwords:
#   Email: test@test.fr
#   Username: test
#   Password: test123
#
#   Email: test2@test.fr
#   Username: test2
#   Password: test123

import os
import sys
from datetime import datetime, timedelta
from random import randint, choice, choices, sample
from pathlib import Path
from dotenv import load_dotenv

# Add app directory to path (works regardless of where the script is run from)
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import (
    Base,
    User,
    Post,
    Comment,
    Like,
    Follow,
    Block,
    Notification,
    Conversation,
    Message,
)

# Load environment variables (find .env in parent directories)
from dotenv import find_dotenv
load_dotenv(find_dotenv())

# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme")
POSTGRES_DB = os.getenv("POSTGRES_DB", "transcendence")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create the database engine and ensure tables exist before seeding
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)

# Sample data
USERNAMES = [
    "alice", "bob", "charlie", "diana", "eve", "frank", "grace", "henry",
    "ivy", "jack", "kate", "leo", "mona", "nate", "olivia"
]

DISPLAY_NAMES = [
    "Alice Wonder", "Bob Smith", "Charlie Brown", "Diana Prince", "Eve Adams",
    "Frank Miller", "Grace Lee", "Henry Ford", "Ivy Green", "Jack Ryan",
    "Kate Bush", "Leo Messi", "Mona Lisa", "Nate Dogg", "Olivia Newton"
]

BIOS = [
    "🎨 Creative designer and coffee lover ☕",
    "📚 Tech enthusiast, always learning something new",
    "🎮 Gamer at heart, streamer wannabe",
    "✈️ Traveling the world one city at a time",
    "💪 Fitness junkie, meal prep expert",
    "🎵 Musician, producer, and music lover",
    "📸 Photography and nature enthusiast",
    "🧠 Science nerd with a passion for coding",
    "🎬 Movie buff and cinema connoisseur",
    "🌱 Environmental activist and eco-warrior",
    "🏋️ Gym rat and personal trainer",
    "🎪 Comedian and entertainer",
    "📱 Tech blogger and podcast host",
    "🌍 Globetrotter and adventure seeker",
    "🍕 Food blogger and cooking enthusiast"
]

POST_CONTENTS = [
    "Just finished an amazing project! Feeling so accomplished 🎉",
    "Can't believe it's already Friday! What are your weekend plans?",
    "Coffee number 3 today ☕☕☕ Send help!",
    "The sunset today was absolutely breathtaking 🌅",
    "Finally fixed that bug that's been haunting me for weeks!",
    "Thoughts on the latest tech trends? I'm curious what everyone thinks...",
    "Starting a new hobby today. Wish me luck! 🤞",
    "This movie was incredible, highly recommend! 🎬",
    "Meal prep Sundays are a game changer 💪",
    "Just learned something new in Python. Mind blown! 🤯",
    "The weather is perfect for a walk. Who else loves autumn?",
    "Finished my first 5K run! So proud of myself! 🏃",
    "Anyone else addicted to this new game? It's so good!",
    "Can we talk about how good this music video is?",
    "Working on a new design. Still deciding on the color scheme...",
    "The mountain view this morning was absolutely stunning 🏔️",
    "Just got back from an amazing trip. Already missing it!",
    "Who else is a night owl like me? 🦉",
    "Coffee tastes better when you make it yourself ☕",
    "That feeling when your code compiles on the first try ✨",
    "Anyone want to collaborate on a project? Let me know!",
    "The gym has been calling my name. Time to get back to it!",
    "Just discovered this amazing restaurant. Food was incredible! 🍽️",
    "Streaming some games later, come hang out!",
    "Book recommendations? Currently looking for something good to read",
    "The new update looks amazing! Have you tried it yet?",
    "Can't stop thinking about this idea for a project...",
    "Just finished a great workout session! 💯",
    "The creativity is flowing today. Best day ever!",
    "Who else struggles with procrastination? Tips welcome! 😅",
]

COMMENTS = [
    "Haha, I love this! 😂",
    "Same here! How did you manage it?",
    "This is amazing! 🔥",
    "I totally agree with you!",
    "Cool post! Thanks for sharing",
    "Wow, that sounds incredible!",
    "I need to try this too!",
    "Couldn't agree more! 👏",
    "This made my day! 😊",
    "Absolutely love this energy!",
    "Goals right here! 💯",
    "So jealous right now!",
    "This is exactly what I needed to see today",
    "You're doing amazing! Keep it up!",
    "So true! Thanks for the reminder",
    "Where did you find this? It's awesome!",
    "I'm trying this today!",
    "Best post I've seen all day",
    "This deserves more attention!",
    "Love the positivity! Keep shining! ✨",
]


def hash_pass(password: str) -> str:
    """Hash password using bcrypt."""
    import bcrypt
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def seed_database(reset=False):
    """Populate database with test data."""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        if reset:
            # Clear existing data
            print("🧹 Clearing existing data...")
            db.query(Notification).delete()
            db.query(Message).delete()
            db.query(Conversation).delete()
            db.query(Like).delete()
            db.query(Comment).delete()
            db.query(Post).delete()
            db.query(Block).delete()
            db.query(Follow).delete()
            db.query(User).delete()
            db.commit()
            print("✓ Database cleared")

        base_time = datetime.utcnow()

        # Create users (upsert by username)
        print("\n👥 Creating users...")
        users = []
        created_users = 0

        test_accounts = [
            {
                "username": "test",
                "email": "test@test.fr",
                "display_name": "Test User",
                "password": "test123",
                "bio": "Test account for manual login.",
            },
            {
                "username": "test2",
                "email": "test2@test.fr",
                "display_name": "Test User 2",
                "password": "test123",
                "bio": "Second test account for manual login.",
            },
        ]

        for account in test_accounts:
            user = db.query(User).filter(User.username == account["username"]).first()
            if not user:
                user = User(
                    username=account["username"],
                    email=account["email"],
                    hashed_password=hash_pass(account["password"]),
                    display_name=account["display_name"],
                    bio=account["bio"],
                    avatar_url="/def_user.png",
                    is_active=True,
                    created_at=base_time - timedelta(days=randint(1, 30)),
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                created_users += 1
            users.append(user)

        for username, display_name, bio in zip(USERNAMES, DISPLAY_NAMES, BIOS):
            user = db.query(User).filter(User.username == username).first()
            if not user:
                user = User(
                    username=username,
                    email=f"{username}@example.com",
                    hashed_password=hash_pass("password123"),
                    display_name=display_name,
                    bio=bio,
                    avatar_url="/def_user.png",
                    is_active=True,
                    created_at=base_time - timedelta(days=randint(1, 30)),
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                created_users += 1
            users.append(user)

        print(f"✓ Users prêts: {len(users)} ({created_users} créés, {len(users) - created_users} déjà existants)")

        # Create posts (complement up to 30)
        print("\n📝 Creating posts...")
        posts = db.query(Post).all()
        created_posts = 0
        target_posts = 30
        to_create = max(0, target_posts - len(posts))

        for _ in range(to_create):
            post = Post(
                content=choice(POST_CONTENTS),
                author_id=choice(users).id,
                created_at=base_time - timedelta(days=randint(0, 15), hours=randint(0, 23)),
            )
            posts.append(post)
            db.add(post)
            created_posts += 1

        db.commit()
        print(f"✓ Posts prêts: {len(posts)} ({created_posts} créés)")

        # Create comments (complement up to 50)
        print("\n💬 Creating comments...")
        comment_count = db.query(Comment).count()
        created_comments = 0
        target_comments = 50
        to_create = max(0, target_comments - comment_count)

        for _ in range(to_create):
            comment = Comment(
                content=choice(COMMENTS),
                post_id=choice(posts).id,
                author_id=choice(users).id,
                created_at=base_time - timedelta(days=randint(0, 15), hours=randint(0, 23)),
            )
            db.add(comment)
            created_comments += 1

        db.commit()
        print(f"✓ Comments prêts: {comment_count + created_comments} ({created_comments} créés)")

        # Create likes (upsert by post_id + user_id)
        print("\n❤️ Creating likes...")
        created_likes = 0
        for post in posts:
            for user in sample(users, randint(1, min(8, len(users)))):
                existing = db.query(Like).filter(
                    Like.post_id == post.id,
                    Like.user_id == user.id
                ).first()
                if not existing:
                    like = Like(
                        post_id=post.id,
                        user_id=user.id,
                        created_at=base_time - timedelta(days=randint(0, 15)),
                    )
                    db.add(like)
                    created_likes += 1

        db.commit()
        total_likes = db.query(Like).count()
        print(f"✓ Likes prêts: {total_likes} ({created_likes} créés)")

        # Create follows (upsert by follower_id + followed_id)
        print("\n👫 Creating follows...")
        created_follows = 0
        for user in users:
            targets = sample(
                [u for u in users if u.id != user.id],
                randint(3, min(8, len(users) - 1))
            )
            for target in targets:
                existing = db.query(Follow).filter(
                    Follow.follower_id == user.id,
                    Follow.followed_id == target.id
                ).first()
                if not existing:
                    follow = Follow(
                        follower_id=user.id,
                        followed_id=target.id,
                        created_at=base_time - timedelta(days=randint(0, 30)),
                    )
                    db.add(follow)
                    created_follows += 1

        db.commit()
        total_follows = db.query(Follow).count()
        print(f"✓ Follows prêts: {total_follows} ({created_follows} créés)")

        # Create blocks (upsert by blocker_id + blocked_id)
        print("\n🚫 Creating blocks...")
        created_blocks = 0
        for user in users:
            if choice([True, False, False]):  # 33% chance
                targets = sample(
                    [u for u in users if u.id != user.id],
                    randint(0, 2)
                )
                for target in targets:
                    existing = db.query(Block).filter(
                        Block.blocker_id == user.id,
                        Block.blocked_id == target.id
                    ).first()
                    if not existing:
                        block = Block(
                            blocker_id=user.id,
                            blocked_id=target.id,
                        )
                        db.add(block)
                        created_blocks += 1

        db.commit()
        total_blocks = db.query(Block).count()
        print(f"✓ Blocks prêts: {total_blocks} ({created_blocks} créés)")

        # Print summary
        print("\n" + "="*50)
        print("✨ Database seeded successfully! ✨")
        print("="*50)
        print(f"📊 Summary:")
        print(f"   • Users:    {len(users)}")
        print(f"   • Posts:    {len(posts)}")
        print(f"   • Comments: {comment_count + created_comments}")
        print(f"   • Likes:    {total_likes}")
        print(f"   • Follows:  {total_follows}")
        print(f"   • Blocks:   {total_blocks}")
        print("="*50)
        print("\n🔐 Test credentials:")
        print("   Email:    test@test.fr  /  test2@test.fr")
        print("   Password: test123")
        print("   (other users: password123)")
        print("="*50)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed the database with test data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Vider complètement la DB avant de seed (ATTENTION: supprime toutes les données)"
    )
    args = parser.parse_args()

    if args.reset:
        confirm = input("⚠️  Voulez-vous vraiment vider la DB ? (oui/non) : ")
        if confirm.strip().lower() != "oui":
            print("Annulé.")
            sys.exit(0)

    seed_database(reset=args.reset)