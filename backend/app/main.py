from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.documents.router import router as document_router
from app.notifications.router import router as notification_router


app = FastAPI(
    title="Document Management System API",
    description="API for managing documents with versioning and permissions",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    document_router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)

app.include_router(
    notification_router,
    prefix="/api/v1/notifications",
    tags=["Notifications"]
)


@app.get("/")
def root():
    return {
        "message": "Document Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
