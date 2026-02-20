import os

from typing import Optional
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm.exc import StaleDataError

from .repository import DocumentRepository
from .models import DocumentStatus, RequestType, RequestStatus
from .schemas import DocumentCreate, DocumentUpdate, DocumentListResponse
from app.notifications.service import NotificationService
from app.core.storage import StorageClient, generate_unique_filename


# Allowed document file extensions
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.rtf', '.odt', '.ods', '.odp', '.csv'
}


def validate_document_file(file: UploadFile):
    """Validate that uploaded file is a document"""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is required"
        )
    
    _, extension = os.path.splitext(file.filename)
    extension = extension.lower()
    
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )


class DocumentService:
    def __init__(
        self, 
        repository: DocumentRepository,
        storage_client: StorageClient,
        notification_service: Optional[NotificationService] = None
    ):
        self.repository = repository
        self.storage_client = storage_client
        self.notification_service = notification_service

    async def upload_document(
        self, 
        document_data: DocumentCreate, 
        file: UploadFile, 
        user_id: int
    ):
        validate_document_file(file)

        object_name = generate_unique_filename(file.filename, user_id)
        
        # Upload to storage
        file_url = self.storage_client.upload_file(
            file.file,
            object_name,
            content_type=file.content_type or "application/octet-stream"
        )
        
        # Get file info
        file_info = self.storage_client.get_file_info(object_name)
        file_size = file_info.size
        
        # Create document record
        document = self.repository.create_document(
            document_data=document_data,
            file_url=file_url,
            file_name=file.filename,
            file_size=file_size,
            user_id=user_id
        )
        
        return document

    def get_document(self, document_id: int, user_id: int, is_admin: bool = False):
        document = self.repository.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check access (owner or admin can view)
        if not is_admin and document.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this document"
            )
        
        return document

    def get_document_download_url(self, document_id: int, user_id: int, is_admin: bool = False) -> str:
        """Get presigned URL for document download"""
        document = self.get_document(document_id, user_id, is_admin)
        
        # Extract object name from file_url (bucket/object_name)
        object_name = document.file_url.split('/', 1)[1] if '/' in document.file_url else document.file_url
        
        # Generate presigned URL (valid for 1 hour)
        download_url = self.storage_client.get_download_url(object_name, expires=3600)
        
        return download_url

    def list_documents(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        document_type: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        is_admin: bool = False
    ) -> DocumentListResponse:
        skip = (page - 1) * page_size
        
        # If not admin, filter by user_id
        filter_user_id = None if is_admin else user_id
        
        documents, total = self.repository.get_documents(
            skip=skip,
            limit=page_size,
            search=search,
            document_type=document_type,
            status=status,
            user_id=filter_user_id
        )
        
        total_pages = (total + page_size - 1) // page_size
        
        return DocumentListResponse(
            items=documents,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def update_document(self, document_id: int, document_data: DocumentUpdate, user_id: int, is_admin: bool = False):
        document = self.repository.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check ownership
        if not is_admin and document.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this document"
            )
        
        # Check if document is locked
        if document.status in [DocumentStatus.PENDING_DELETE, DocumentStatus.PENDING_REPLACE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is locked pending approval"
            )
        
        return self.repository.update_document(document_id, document_data)

    async def delete_document(self, document_id: int):
        """Admin direct delete - no approval needed"""
        document = self.repository.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete file from storage
        if document.file_url:
            object_name = document.file_url.split('/', 1)[1] if '/' in document.file_url else document.file_url
            try:
                self.storage_client.delete_file(object_name)
            except Exception:
                pass
        
        # Delete from database
        self.repository.delete_document(document_id)

    async def replace_document(self, document_id: int, file: UploadFile):
        """Admin direct replace - no approval needed"""
        validate_document_file(file)
        
        document = self.repository.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found"
            )
        
        # Upload new file
        object_name = generate_unique_filename(file.filename, document.created_by)
        
        file_url = self.storage_client.upload_file(
            file.file,
            object_name,
            content_type=file.content_type or "application/octet-stream"
        )
        
        # Delete old file
        if document.file_url:
            old_object_name = document.file_url.split('/', 1)[1] if '/' in document.file_url else document.file_url
            try:
                self.storage_client.delete_file(old_object_name)
            except Exception:
                pass
        
        # Update document
        return self.repository.replace_document_file(
            document_id,
            file_url,
            file.filename,
            file.size
        )

    async def request_delete(self, document_id: int, user_id: int, reason: Optional[str] = None):
        document = self.repository.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check ownership
        if document.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this document"
            )
        
        # Check if already pending
        if document.status in [DocumentStatus.PENDING_DELETE, DocumentStatus.PENDING_REPLACE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document already has a pending request"
            )
        
        try:
            # Create permission request
            permission_request = self.repository.create_permission_request(
                document_id=document_id,
                user_id=user_id,
                request_type=RequestType.DELETE,
                reason=reason
            )
            
            # Update document status (will fail if version changed)
            self.repository.update_document_status(document_id, DocumentStatus.PENDING_DELETE)
            
            # Send notification to admins
            if self.notification_service:
                await self.notification_service.notify_admins(
                    f"Delete request for document: {document.title}",
                    f"User requested to delete document '{document.title}'. Reason: {reason or 'No reason provided'}"
                )
            
            return permission_request
        except StaleDataError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document was modified by another request. Please try again."
            )

    async def request_replace(
        self, 
        document_id: int, 
        file: UploadFile, 
        user_id: int, 
        reason: Optional[str] = None
    ):
        validate_document_file(file)
        
        document = self.repository.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check ownership
        if document.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to replace this document"
            )
        
        # Check if already pending
        if document.status in [DocumentStatus.PENDING_DELETE, DocumentStatus.PENDING_REPLACE]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document already has a pending request"
            )
        
        # Upload new file to temporary location
        temp_object_name = f"temp/{generate_unique_filename(file.filename, user_id)}"
        temp_file_url = self.storage_client.upload_file(
            file.file,
            temp_object_name,
            content_type=file.content_type or "application/octet-stream"
        )
        
        try:
            # Create permission request
            permission_request = self.repository.create_permission_request(
                document_id=document_id,
                user_id=user_id,
                request_type=RequestType.REPLACE,
                reason=reason,
                new_file_url=temp_file_url
            )
            
            # Update document status (will fail if version changed)
            self.repository.update_document_status(document_id, DocumentStatus.PENDING_REPLACE)
            
            # Send notification to admins
            if self.notification_service:
                await self.notification_service.notify_admins(
                    f"Replace request for document: {document.title}",
                    f"User requested to replace document '{document.title}'. Reason: {reason or 'No reason provided'}"
                )
            
            return permission_request
        except StaleDataError:
            # Cleanup uploaded temp file if conflict
            try:
                self.storage_client.delete_file(temp_object_name)
            except:
                pass
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document was modified by another request. Please try again."
            )

    async def approve_request(self, request_id: int, admin_id: int):
        permission_request = self.repository.get_permission_request(request_id)
        if not permission_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission request not found"
            )
        
        if permission_request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request already processed"
            )
        
        document = self.repository.get_document(permission_request.document_id)
        
        # Update request status first
        updated_request = self.repository.update_permission_request_status(
            request_id,
            RequestStatus.APPROVED,
            admin_id
        )
        
        # Process based on request type
        if permission_request.request_type == RequestType.DELETE:
            # Delete file from storage
            if document.file_url:
                object_name = document.file_url.split('/', 1)[1] if '/' in document.file_url else document.file_url
                try:
                    self.storage_client.delete_file(object_name)
                except Exception as e:
                    print(f"Warning: Could not delete file from file storage: {e}")
            
            # Delete document from database
            self.repository.delete_document(permission_request.document_id)
        
        elif permission_request.request_type == RequestType.REPLACE:
            # Get old and new file info
            old_object_name = document.file_url.split('/', 1)[1] if '/' in document.file_url else document.file_url
            new_object_name = permission_request.new_file_url.split('/', 1)[1] if '/' in permission_request.new_file_url else permission_request.new_file_url
            
            # Get new file info
            file_info = self.storage_client.get_file_info(new_object_name)
            file_size = file_info.size
            
            # Get new filename from temp path
            file_name = new_object_name.split('/')[-1]
            
            # Replace document file
            self.repository.replace_document_file(
                permission_request.document_id,
                permission_request.new_file_url,
                file_name,
                file_size
            )
            
            # Delete old file from storage
            try:
                self.storage_client.delete_file(old_object_name)
            except Exception as e:
                print(f"Warning: Could not delete old file from file storage: {e}")
        
        # Notify requester
        if self.notification_service:
            await self.notification_service.create_notification(
                user_id=permission_request.requested_by,
                title="Request Approved",
                message=f"Your {permission_request.request_type.value} request has been approved."
            )
        
        return updated_request

    async def reject_request(self, request_id: int, admin_id: int):
        permission_request = self.repository.get_permission_request(request_id)
        if not permission_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission request not found"
            )
        
        if permission_request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request already processed"
            )
        
        # Update request status
        self.repository.update_permission_request_status(
            request_id,
            RequestStatus.REJECTED,
            admin_id
        )
        
        # Restore document status
        self.repository.update_document_status(
            permission_request.document_id,
            DocumentStatus.ACTIVE
        )
        
        # Clean up temp file if replace request
        if permission_request.request_type == RequestType.REPLACE and permission_request.new_file_url:
            temp_object_name = permission_request.new_file_url.split('/', 1)[1] if '/' in permission_request.new_file_url else permission_request.new_file_url
            try:
                self.storage_client.delete_file(temp_object_name)
            except Exception as e:
                print(f"Warning: Could not delete temp file from file storage: {e}")
        
        # Notify requester
        if self.notification_service:
            await self.notification_service.create_notification(
                user_id=permission_request.requested_by,
                title="Request Rejected",
                message=f"Your {permission_request.request_type.value} request has been rejected."
            )
        
        return permission_request

    def list_pending_requests(self, page: int = 1, page_size: int = 10):
        skip = (page - 1) * page_size
        requests, total = self.repository.get_pending_permission_requests(skip, page_size)
        
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "items": requests,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

