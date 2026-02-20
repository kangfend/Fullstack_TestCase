"""
Database initialization script
Run this to create all tables
"""
from app.core.database import Base, engine

from app.auth.models import User
from app.documents.models import Document, PermissionRequest
from app.notifications.models import Notification


def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
