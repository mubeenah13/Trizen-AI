from pydantic import BaseModel, Field
from typing import List, Optional

class PublicGalleryVerifyRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=8, example="123456")

class PublicGalleryVerifyResponse(BaseModel):
    gallery_access_token: str
    token_type: str = "bearer"
    gallery_name: str
    event_name: str
    photo_count: int

class PublicGalleryMetaResponse(BaseModel):
    name: str
    slug: str
    event_name: str
    event_date: str
    photo_count: int
    is_protected: bool = True

class PublicPhotoResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    mime_type: str
    url: str
    created_at: str
