"""
MinIO implementation of StorageClient
"""
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from app.core.storage import StorageClient
import io
from typing import BinaryIO


class MinIOClient(StorageClient):
    """MinIO implementation of StorageClient for S3-compatible object storage"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error:
            raise
    
    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """Upload file to MinIO"""
        try:
            file_data.seek(0, io.SEEK_END)
            file_size = file_data.tell()
            file_data.seek(0)
            
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_data,
                length=file_size,
                content_type=content_type,
                part_size=10 * 1024 * 1024  # 10MB chunks for large files
            )
            
            return f"{self.bucket_name}/{object_name}"
        except S3Error:
            raise
    
    def delete_file(self, object_name: str):
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
        except S3Error:
            raise
    
    def get_download_url(self, object_name: str, expires: int = 3600) -> str:
        """Get presigned URL for file download"""
        try:
            return self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
        except S3Error:
            raise
    
    def get_file_info(self, object_name: str):
        """Get file metadata from MinIO"""
        try:
            return self.client.stat_object(self.bucket_name, object_name)
        except S3Error:
            raise


def get_storage_client() -> StorageClient:
    """Factory function to get storage client instance"""
    return MinIOClient()
