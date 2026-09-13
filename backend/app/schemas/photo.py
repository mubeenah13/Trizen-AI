from pydantic import BaseModel, Field
from typing import Optional

class PhotoResponse(BaseModel):
    id: str
    event_id: str
    uploaded_by: str
    uploader_name: Optional[str] = None
    filename: str
    storage_key: str
    url: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: str

    class Config:
        from_attributes = True

class BulkPhotoSelectRequest(BaseModel):
    photo_ids: list[str]
