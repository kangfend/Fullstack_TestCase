from .repository import NotificationRepository
from .schemas import NotificationListResponse


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def create_notification(self, user_id: int, title: str, message: str):
        return self.repository.create_notification(user_id, title, message)

    async def notify_admins(self, title: str, message: str):
        admin_ids = self.repository.get_admin_user_ids()
        for admin_id in admin_ids:
            self.repository.create_notification(admin_id, title, message)

    def get_notifications(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10,
        unread_only: bool = False
    ) -> NotificationListResponse:
        skip = (page - 1) * page_size
        
        notifications, total, unread_count = self.repository.get_user_notifications(
            user_id=user_id,
            skip=skip,
            limit=page_size,
            unread_only=unread_only
        )
        
        total_pages = (total + page_size - 1) // page_size
        
        return NotificationListResponse(
            items=notifications,
            total=total,
            unread_count=unread_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def mark_as_read(self, notification_id: int, user_id: int):
        return self.repository.mark_as_read(notification_id, user_id)

    def mark_all_as_read(self, user_id: int):
        return self.repository.mark_all_as_read(user_id)
