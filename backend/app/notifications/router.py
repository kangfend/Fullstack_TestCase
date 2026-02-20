from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from .service import NotificationService
from .repository import NotificationRepository
from .schemas import NotificationListResponse, NotificationResponse


router = APIRouter()


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    repository = NotificationRepository(db)
    return NotificationService(repository)


@router.get("/", response_model=NotificationListResponse)
def get_notifications(
    page: int = 1,
    page_size: int = 10,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Get user notifications with pagination"""
    return service.get_notifications(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        unread_only=unread_only
    )


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Mark a notification as read"""
    notification = service.mark_as_read(notification_id, current_user.id)
    if not notification:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return notification


@router.post("/mark-all-read")
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Mark all notifications as read"""
    updated_count = service.mark_all_as_read(current_user.id)
    return {"message": f"Marked {updated_count} notifications as read"}
