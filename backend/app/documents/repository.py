from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime

from .models import Document, PermissionRequest, DocumentStatus, RequestStatus, RequestType
from .schemas import DocumentCreate, DocumentUpdate
from app.auth.models import User


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(self, document_data: DocumentCreate, file_url: str, file_name: str, 
                       file_size: int, user_id: int) -> Document:
        document = Document(
            title=document_data.title,
            description=document_data.description,
            document_type=document_data.document_type,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
            created_by=user_id,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_document(self, document_id: int) -> Optional[Document]:
        return self.db.query(Document).options(joinedload(Document.creator)).filter(Document.id == document_id).first()

    def get_documents(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        document_type: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> tuple[List[Document], int]:
        query = self.db.query(Document).options(joinedload(Document.creator))

        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Document.title.ilike(f"%{search}%"),
                    Document.description.ilike(f"%{search}%")
                )
            )
        
        if document_type:
            query = query.filter(Document.document_type == document_type)
        
        if status:
            query = query.filter(Document.status == status)
        
        if user_id:
            query = query.filter(Document.created_by == user_id)

        total = query.count()
        documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
        
        return documents, total

    def update_document(self, document_id: int, document_data: DocumentUpdate) -> Optional[Document]:
        document = self.get_document(document_id)
        if not document:
            return None

        update_data = document_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)

        self.db.commit()
        self.db.refresh(document)
        return document

    def update_document_status(self, document_id: int, status: DocumentStatus) -> Optional[Document]:
        document = self.get_document(document_id)
        if not document:
            return None
        
        document.status = status
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete_document(self, document_id: int) -> bool:
        document = self.get_document(document_id)
        if not document:
            return False
        
        self.db.delete(document)
        self.db.commit()
        return True

    def replace_document_file(self, document_id: int, file_url: str, file_name: str, 
                             file_size: int) -> Optional[Document]:
        document = self.get_document(document_id)
        if not document:
            return None
        
        document.file_url = file_url
        document.file_name = file_name
        document.file_size = file_size
        document.status = DocumentStatus.ACTIVE
        # Note: version will be auto-incremented by SQLAlchemy optimistic locking
        
        self.db.commit()
        self.db.refresh(document)
        return document

    # Permission Request methods
    def create_permission_request(self, document_id: int, user_id: int, 
                                 request_type: RequestType, reason: Optional[str] = None,
                                 new_file_url: Optional[str] = None) -> PermissionRequest:
        request = PermissionRequest(
            document_id=document_id,
            requested_by=user_id,
            request_type=request_type,
            reason=reason,
            new_file_url=new_file_url
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def get_permission_request(self, request_id: int) -> Optional[PermissionRequest]:
        return self.db.query(PermissionRequest).filter(PermissionRequest.id == request_id).first()

    def get_pending_permission_requests(self, skip: int = 0, limit: int = 10) -> tuple[List[PermissionRequest], int]:
        query = self.db.query(PermissionRequest).filter(
            PermissionRequest.status == RequestStatus.PENDING
        )
        total = query.count()
        requests = query.order_by(PermissionRequest.created_at.desc()).offset(skip).limit(limit).all()
        return requests, total

    def update_permission_request_status(
        self, 
        request_id: int, 
        status: RequestStatus, 
        reviewed_by: int
    ) -> Optional[PermissionRequest]:
        request = self.get_permission_request(request_id)
        if not request:
            return None
        
        request.status = status
        request.reviewed_by = reviewed_by
        request.reviewed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(request)
        return request

