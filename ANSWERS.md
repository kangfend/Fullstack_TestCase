# System Design Q&A

This document contains answers to the system design questions listed in the `README.md` file, based on the current implementation of the Document Management System (DMS).

## 1. How to handle large file uploads?

The system handles file uploads using FastAPI's streaming capabilities and implements validation for security.

### Current Implementation
- **Size Validation:** Enforces a strict file size limit (default 100MB) via `settings.MAX_FILE_SIZE`. The validation check (`file.size`) runs before heavy processing.
- **Type Validation:** Restricts uploads to safe document types (PDF, Office, Text) using an `ALLOWED_EXTENSIONS` whitelist.
- **FastAPI Streaming:** The `UploadFile` type streams content to disk (spooled temp file) rather than memory, preventing RAM exhaustion.
- **MinIO Multipart:** The storage client uploads to MinIO in 10MB chunks.
- **Code Reference:**
  - `backend/app/documents/service.py`: `validate_document_file` function checks extension and size.
  - `backend/app/core/config.py`: Defines `MAX_FILE_SIZE = 100MB`.
  - `backend/app/core/storage/minio.py`: Uses chunked upload.

---

## 2. How to avoid lost updates when replacing documents?

The system implements **Optimistic Locking** to prevent "Lost Update" race conditions where two users might overwrite each other's changes.

### Current Implementation
- **Version Control:** The `Document` model includes a `version` column that automatically increments on every update.
- **Atomic Verification:** Updates utilize SQLAlchemy's versioning feature (`version_id_col`). When an update is attempted, the SQL query strictly checks `WHERE id = X AND version = Y`.
- **Conflict Handling:** If the version in the database doesn't match the version known by the application (meaning another user modified it), a `StaleDataError` is raised.
- **Code Reference:**
  - `backend/app/documents/models.py`: `__mapper_args__ = {"version_id_col": "version"}` configuration.
  - `backend/app/documents/repository.py`: Methods like `update_document` implicitly use this version check during `commit()`.

---

## 3. How to design notification system for scalability?

The current notification system is synchronous and tightly coupled to the application logic. While effective for the initial deployment phase, a transition to an asynchronous architecture will be required to support future growth.

### Current Implementation
- **Synchronous Execution:** Notification creation happens within the main request lifecycle. If a notification fails to save, the user (or caller) is immediately aware.
- **Direct Database Writes:** Notifications are persisted directly to PostgreSQL via the `NotificationRepository`.
- **Polling:** The frontend polls the API (`/api/v1/notifications`) to fetch updates.
- **Code Reference:**
  - `backend/app/notifications/service.py`: Methods execute blocking DB calls to ensure data consistency.

### Scalability Strategy (Migration Plan)
While the synchronous approach is robust for < 1,000 users, high-scale environments (> 10k users) will require decoupling:

2.  **Level 1 (Message Queue):** Introduce a broker (Redis/RabbitMQ) and worker (Celery) to handle notifications independently. This is the recommended path for true scalability as it isolates the main application from notification logic failures.
3.  **Level 2 (Real-time):** Replace polling with WebSockets or Server-Sent Events (SSE).

---

## 4. How to secure file access?

File security is handled through a combination of strict authentication, role-based access control (RBAC), and temporary access URLs.

### Current Implementation
- **Authentication:** All access requires a valid JWT token passed via HTTP-only cookies.
- **Authorization:** The `get_document` service layer enforces logic: Users can only access their own documents; Admins can access all.
- **Presigned URLs:** Files are served via MinIO presigned URLs with a short expiration (1 hour). This means the actual file storage is private and never directly exposed to the internet.
- **Code Reference:**
  - `backend/app/documents/service.py`: Authorization logic checking `user_id` or `is_admin`.
  - `backend/app/core/storage/minio.py`: `get_download_url` generates signed, time-limited URLs.

---

## 5. How to structure services for microservice migration?

The application is structured as a "Modular Monolith," which is the ideal starting point for a system that may eventually need to split into microservices.

### Current Architecture
- **Domain Isolation:** The code is organized by domain (`auth`, `documents`, `notifications`), not by technical layer. Each domain has its own Router, Service, Repository, and Models.
- **Repository Pattern:** Database access is abstracted, allowing the data store to change without affecting business logic.

### Migration Path
When the need arises (e.g., team size grows >10, or traffic spikes >10k RPS), the migration is straightforward:
1.  **Phase 1 (Split):** Take a domain folder (e.g., `notifications`), move it to a new repo.
2.  **Phase 2 (Interface):** Replace the direct service call in the main app with an HTTP client call to the new service.
3.  **Phase 3 (Database):** Split the database schema so the new service owns its own data.
