from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from .repository import AuthRepository
from .schemas import UserCreate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def authenticate_user(self, email: str, password: str):
        user = self.repository.get_user_by_email(email)

        if not user or not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user

    def register_user(self, user_data: UserCreate):
        # Check if user already exists
        existing_user = self.repository.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = self.hash_password(user_data.password)
        user = self.repository.create_user(user_data, hashed_password)
        return user

    def login(self, email: str, password: str):
        user = self.authenticate_user(email, password)
        access_token = self.create_access_token({
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.value
        })
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }