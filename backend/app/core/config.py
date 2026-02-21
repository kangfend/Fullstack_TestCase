from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    # Auth Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # MinIO/S3 Settings
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "dms-documents"
    MINIO_SECURE: bool = False

    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
