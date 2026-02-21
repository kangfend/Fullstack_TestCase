from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from .repository import NotificationRepository
from .service import NotificationService


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    repository = NotificationRepository(db)
    return NotificationService(repository)