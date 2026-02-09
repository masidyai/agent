#!/bin/sh
set -e

echo "Starting Masidy Backend API..."

# Wait for database to be ready (if using external DB)
echo "Checking database connection..."
python -c "
import asyncio
from app.core.database import init_db

async def check_db():
    try:
        await init_db()
        print('Database connection successful')
    except Exception as e:
        print(f'Database check failed: {e}')
        exit(1)

asyncio.run(check_db())
"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Starting uvicorn server..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
