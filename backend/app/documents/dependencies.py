from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.storage.minio import get_storage_client
from app.core.storage import StorageClient
from app.notifications.service import NotificationService
from app.notifications.repository import NotificationRepository

from .repository import DocumentRepository
from .service import DocumentService


def get_document_service(
    db: Session = Depends(get_db),
    storage_client: StorageClient = Depends(get_storage_client)
) -> DocumentService:
    doc_repository = DocumentRepository(db)
    notif_repository = NotificationRepository(db)
    notif_service = NotificationService(notif_repository)
    return DocumentService(doc_repository, storage_client, notif_service)