#!/bin/sh
set -e

echo "Waiting for database to be ready..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done

echo "Database is ready. Seeding database..."
python3 seed_db.py

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
