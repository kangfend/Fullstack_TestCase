from sqlalchemy.orm import Session
from typing import List, Optional
from .models import Notification


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, user_id: int, title: str, message: str) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_user_notifications(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10,
        unread_only: bool = False
    ) -> tuple[List[Notification], int, int]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        total = query.count()
        unread_count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
        
        notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
        
        return notifications, total, unread_count

    def mark_as_read(self, notification_id: int, user_id: int) -> Optional[Notification]:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            return None
        
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, user_id: int) -> int:
        updated = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        self.db.commit()
        return updated

    def get_admin_user_ids(self) -> List[int]:
        from app.auth.models import User, UserRole
        admin_users = self.db.query(User.id).filter(User.role == UserRole.ADMIN).all()
        return [user.id for user in admin_users]
