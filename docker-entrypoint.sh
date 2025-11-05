#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."

# Wait for PostgreSQL to be available
until python -c "from app.core.db.session import engine; engine.connect()" 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done

echo "PostgreSQL is up - executing migrations"

# Run database migrations
alembic upgrade head

echo "Migrations completed - starting application"

# Execute the main command (start the app)
exec "$@"
