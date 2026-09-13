import os
import uuid
import boto3
from botocore.config import Config
from fastapi import HTTPException, status
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.mode = settings.STORAGE_MODE.lower()
        self.bucket = settings.S3_BUCKET_NAME
        self.local_dir = settings.LOCAL_STORAGE_PATH
        os.makedirs(self.local_dir, exist_ok=True)
        self.s3_client = None

        if self.mode == "s3":
            try:
                boto_config = Config(
                    connect_timeout=2,
                    read_timeout=2,
                    retries={'max_attempts': 1}
                )
                self.s3_client = boto3.client(
                    "s3",
                    endpoint_url=settings.S3_ENDPOINT_URL,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    region_name=settings.S3_REGION,
                    use_ssl=settings.S3_USE_SSL,
                    config=boto_config
                )
            except Exception as e:
                print(f"[StorageService] S3 client initialization failed: {e}")
                if settings.ENVIRONMENT == "production":
                    raise RuntimeError("S3 Object Storage initialization failed in production mode.")
                self.mode = "local"

    def upload_file(self, file_bytes: bytes, filename: str, content_type: str, event_id: str) -> dict:
        ext = os.path.splitext(filename)[1].lower()
        unique_id = str(uuid.uuid4())
        storage_key = f"events/{event_id}/{unique_id}{ext}"
        file_size = len(file_bytes)

        if self.mode == "s3" and self.s3_client:
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=storage_key,
                    Body=file_bytes,
                    ContentType=content_type
                )
                storage_url = f"{settings.S3_ENDPOINT_URL}/{self.bucket}/{storage_key}"
                return {
                    "storage_key": storage_key,
                    "storage_url": storage_url,
                    "file_size": file_size
                }
            except Exception as e:
                print(f"[StorageService] S3 upload error: {e}")
                if settings.ENVIRONMENT == "production":
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Production S3 Object Storage is temporarily unavailable. Upload aborted."
                    )
                # In development mode, fallback to local storage
                return self._upload_local(file_bytes, storage_key, file_size)
        else:
            return self._upload_local(file_bytes, storage_key, file_size)

    def _upload_local(self, file_bytes: bytes, storage_key: str, file_size: int) -> dict:
        safe_name = storage_key.replace("/", "_")
        full_path = os.path.join(self.local_dir, safe_name)
        with open(full_path, "wb") as f:
            f.write(file_bytes)
        storage_url = f"/api/v1/photos/local-stream/{safe_name}"
        return {
            "storage_key": storage_key,
            "storage_url": storage_url,
            "file_size": file_size
        }

    def delete_file(self, storage_key: str) -> bool:
        if self.mode == "s3" and self.s3_client:
            try:
                self.s3_client.delete_object(Bucket=self.bucket, Key=storage_key)
                return True
            except Exception:
                pass
        safe_name = storage_key.replace("/", "_")
        full_path = os.path.join(self.local_dir, safe_name)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def get_file_bytes(self, storage_key: str) -> bytes:
        if self.mode == "s3" and self.s3_client:
            try:
                response = self.s3_client.get_object(Bucket=self.bucket, Key=storage_key)
                return response["Body"].read()
            except Exception as e:
                if settings.ENVIRONMENT == "production":
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Object storage media retrieval failed."
                    )
        
        safe_name = storage_key.replace("/", "_")
        full_path = os.path.join(self.local_dir, safe_name)
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                return f.read()
        
        dummy_svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="100%" height="100%" fill="#1e293b"/><text x="50%" y="50%" fill="#38bdf8" font-size="32" text-anchor="middle" font-family="sans-serif">Sample Photo ({storage_key})</text></svg>'
        return dummy_svg.encode("utf-8")

storage_service = StorageService()
