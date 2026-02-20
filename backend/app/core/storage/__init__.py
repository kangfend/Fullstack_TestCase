"""
Storage abstraction layer for file operations.
Supports multiple storage backends (MinIO, S3, GCS, etc.)
"""
from abc import ABC, abstractmethod
from typing import BinaryIO
import uuid


class StorageClient(ABC):
    """Abstract base class for storage operations"""
    
    @abstractmethod
    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload file to storage"""
        pass
    
    @abstractmethod
    def delete_file(self, object_name: str):
        """Delete file from storage"""
        pass
    
    @abstractmethod
    def get_download_url(self, object_name: str, expires: int = 3600) -> str:
        """Get presigned URL for file download"""
        pass
    
    @abstractmethod
    def get_file_info(self, object_name: str):
        """Get file metadata"""
        pass


def generate_unique_filename(original_filename: str, user_id: int) -> str:
    """Generate unique filename for storage"""
    parts = original_filename.rsplit('.', 1)
    extension = parts[1] if len(parts) > 1 else ''
    unique_id = str(uuid.uuid4())
    return f"{user_id}/{unique_id}.{extension}" if extension else f"{user_id}/{unique_id}"
