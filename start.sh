#!/bin/sh

echo "⏳ Waiting for Postgres at $DB_HOST:$DB_PORT..."

# Keep trying until Postgres is ready
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done

echo "✅ Postgres is up! Running migrations..."

alembic revision --autogenerate -m "Create User table" 
# Run alembic migrations
alembic upgrade head

echo "🚀 Starting FastAPI app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
