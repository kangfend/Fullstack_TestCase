from fastapi import APIRouter, Depends, status, UploadFile, File, Query, Form
from typing import Optional


from app.auth.dependencies import get_current_user, require_admin
from app.auth.models import User, UserRole
from .dependencies import get_document_service
from .service import DocumentService
from .schemas import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse,
    PermissionRequestResponse, PermissionRequestListResponse
)



router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service)
):
    """Upload a new document"""
    document_data = DocumentCreate(
        title=title,
        description=description,
        document_type=document_type
    )
    return await service.upload_document(document_data, file, current_user.id)


@router.get("/", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service)
):
    """List documents with pagination and filters"""
    is_admin = current_user.role == UserRole.ADMIN
    return service.list_documents(
        page=page,
        page_size=page_size,
        search=search,
        document_type=document_type,
        status=status,
        user_id=current_user.id,
        is_admin=is_admin
    )


@router.get("/permissions/pending", response_model=PermissionRequestListResponse)
def list_pending_permission_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_admin),
    service: DocumentService = Depends(get_document_service)
):
    """List all pending permission requests (Admin only)"""
    return service.list_pending_requests(page, page_size)


@router.post("/permissions/{request_id}/approve", response_model=PermissionRequestResponse)
async def approve_permission_request(
    request_id: int,
    current_user: User = Depends(require_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Approve a permission request (Admin only)"""
    return await service.approve_request(request_id, current_user.id)


@router.post("/permissions/{request_id}/reject", response_model=PermissionRequestResponse)
async def reject_permission_request(
    request_id: int,
    current_user: User = Depends(require_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Reject a permission request (Admin only)"""
    return await service.reject_request(request_id, current_user.id)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service)
):
    """Get document details"""
    is_admin = current_user.role == UserRole.ADMIN
    return service.get_document(document_id, current_user.id, is_admin)


@router.get("/{document_id}/download-url")
def get_document_download_url(
    document_id: int,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service)
):
    """Get presigned URL for document download (valid for 1 hour)"""
    is_admin = current_user.role == UserRole.ADMIN
    download_url = service.get_document_download_url(document_id, current_user.id, is_admin)
    return {
        "download_url": download_url,
        "expires_in": 3600,
        "message": "Use this URL to download the file. Valid for 1 hour."
    }


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service)
):
    """Update document metadata"""
    is_admin = current_user.role == UserRole.ADMIN
    return service.update_document(document_id, document_data, current_user.id, is_admin)


@router.post("/{document_id}/request-delete", response_model=PermissionRequestResponse)
async def request_delete_document(
    document_id: int,
    reason: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service)
):
    """Request permission to delete a document"""
    return await service.request_delete(document_id, current_user.id, reason)


@router.post("/{document_id}/request-replace", response_model=PermissionRequestResponse)
async def request_replace_document(
    document_id: int,
    file: UploadFile = File(...),
    reason: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service)
):
    """Request permission to replace a document"""
    return await service.request_replace(document_id, file, current_user.id, reason)


# Admin direct actions
@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(require_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Delete a document directly (Admin only)"""
    await service.delete_document(document_id)
    return None


@router.post("/{document_id}/replace", response_model=DocumentResponse)
async def replace_document(
    document_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    service: DocumentService = Depends(get_document_service)
):
    """Replace a document file directly (Admin only)"""
    return await service.replace_document(document_id, file)
