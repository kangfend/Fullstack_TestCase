"""
Create initial admin and demo users
"""
from app.core.database import SessionLocal
from app.auth.models import User, UserRole
from app.auth.service import AuthService
from app.auth.repository import AuthRepository
from app.auth.schemas import UserCreate
from app.init_db import init_db


def create_admin_user():
    """Create an initial admin user"""
    init_db()
    
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == "admin@dms.com").first()
        if existing_admin:
            print("Admin user already exists!")
            return
        
        repository = AuthRepository(db)
        service = AuthService(repository)
        
        admin_data = UserCreate(
            email="admin@dms.com",
            full_name="Admin User",
            password="admin123"
        )
        
        user = service.register_user(admin_data)
        user.role = UserRole.ADMIN
        db.commit()
        
        print("Admin user created successfully!")
        print("Email: admin@dms.com")
        print("Password: admin123")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def create_demo_user():
    """Create a demo regular user"""
    init_db()
    
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == "user@dms.com").first()
        if existing_user:
            print("Demo user already exists!")
            return
        
        repository = AuthRepository(db)
        service = AuthService(repository)
        
        user_data = UserCreate(
            email="user@dms.com",
            full_name="Demo User",
            password="user123"
        )
        
        service.register_user(user_data)
        
        print("Demo user created successfully!")
        print("Email: user@dms.com")
        print("Password: user123")
        
    except Exception as e:
        print(f"Error creating demo user: {e}")
        db.rollback()
    finally:
        db.close()


def create_all_users():
    """Create both admin and demo user"""
    create_admin_user()
    create_demo_user()


if __name__ == "__main__":
    create_all_users()
