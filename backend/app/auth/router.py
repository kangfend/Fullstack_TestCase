from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from .schemas import UserCreate, UserLogin, UserResponse
from .service import AuthService
from .repository import AuthRepository
from .dependencies import get_current_user
from .models import User


router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    repository = AuthRepository(db)
    return AuthService(repository)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    return service.register_user(user_data)


@router.post("/login")
def login(
    credentials: UserLogin,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    result = service.login(credentials.email, credentials.password)
    
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=False,  # Set True in production with HTTPS
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {
        "message": "Login successful"
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info - also used to verify session"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value
    }

