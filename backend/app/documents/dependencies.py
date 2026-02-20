from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from .repository import DocumentRepository
from .service import DocumentService


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    repository = DocumentRepository(db)
    return DocumentService(repository)
