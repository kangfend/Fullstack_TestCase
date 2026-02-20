from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any
from datetime import datetime


class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    document_type: str = Field(..., min_length=1, max_length=100)


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    document_type: Optional[str] = Field(None, min_length=1, max_length=100)


class DocumentResponse(DocumentBase):
    id: int
    file_url: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    version: int
    status: str
    created_by: int
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
    
    @model_validator(mode='before')
    @classmethod
    def extract_creator_name(cls, data: Any) -> Any:
        if hasattr(data, 'creator') and data.creator:
            return {
                'id': data.id,
                'title': data.title,
                'description': data.description,
                'document_type': data.document_type,
                'file_url': data.file_url,
                'file_name': data.file_name,
                'file_size': data.file_size,
                'version': data.version,
                'status': data.status.value if hasattr(data.status, 'value') else data.status,
                'created_by': data.created_by,
                'created_by_name': data.creator.full_name,
                'created_at': data.created_at,
                'updated_at': data.updated_at,
            }
        return data


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PermissionRequestResponse(BaseModel):
    id: int
    document_id: int
    requested_by: int
    request_type: str
    status: str
    reason: Optional[str]
    new_file_url: Optional[str]
    created_at: datetime
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True


class PermissionRequestListResponse(BaseModel):
    items: list[PermissionRequestResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
