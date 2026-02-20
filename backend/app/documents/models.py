from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import UpdateBase
from app.core.database import Base
import enum


class DocumentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING_DELETE = "PENDING_DELETE"
    PENDING_REPLACE = "PENDING_REPLACE"


class RequestType(str, enum.Enum):
    DELETE = "DELETE"
    REPLACE = "REPLACE"


class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Document(Base):
    __tablename__ = "documents"
    __mapper_args__ = {"version_id_col": "version"}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(String(500))
    document_type = Column(String(100), nullable=False, index=True)
    file_url = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)
    version = Column(Integer, default=1, nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.ACTIVE, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __mapper_args__ = {"version_id_col": version}

    # Relationships
    permission_requests = relationship("PermissionRequest", back_populates="document")
    creator = relationship("User", foreign_keys=[created_by])


class PermissionRequest(Base):
    __tablename__ = "permission_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_type = Column(SQLEnum(RequestType), nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    reason = Column(String(500))
    new_file_url = Column(String(500))  # For REPLACE type
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))

    # Relationships
    document = relationship("Document", back_populates="permission_requests", lazy="noload")
