import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "TrizenAI Photo Sharing Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Database Configuration (SQLite default for local execution without Docker Postgres)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "trizen_photos"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "sqlite+aiosqlite:///./trizen_photos.db"
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./trizen_photos_test.db"
    
    # JWT Security
    JWT_SECRET_KEY: str = "supersecretjwtkeyforphotosharingplatformchangeinproduction"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # Gallery Access Token
    GALLERY_JWT_SECRET_KEY: str = "supersecretgalleryjwtkeyforcustomeraccess"
    GALLERY_TOKEN_EXPIRE_MINUTES: int = 120
    
    # S3 Object Storage
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "trizen-photos-bucket"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False
    
    # Storage Mode ("s3" or "local")
    STORAGE_MODE: str = "local"
    LOCAL_STORAGE_PATH: str = "./uploads"
    
    # Security Brute Force Settings
    MAX_PIN_ATTEMPTS: int = 5
    PIN_LOCKOUT_MINUTES: int = 15

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
