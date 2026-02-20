#!/bin/bash
set -e

echo "🔄 Initializing database..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until python -c "from sqlalchemy import create_engine; import os; engine = create_engine(os.environ['DATABASE_URL']); engine.connect()" 2>/dev/null; do
  sleep 2
done

echo "✅ PostgreSQL is ready"

# Initialize database tables
echo "📋 Creating database tables..."
python -m app.init_db

# Create default users if they don't exist
echo "👤 Creating default users..."
python -m app.create_users || echo "ℹ️  Users already exist"

echo "🚀 Starting application..."
echo ""

# Execute the CMD from Dockerfile or docker-compose
exec "$@"
