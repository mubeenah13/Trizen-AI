from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.gallery import GalleryStatus

class GalleryCreateRequest(BaseModel):
    event_id: str = Field(..., example="event-uuid-here")
    name: str = Field(..., min_length=2, max_length=200, example="Highlights Gallery")
    pin: str = Field(..., min_length=4, max_length=8, example="123456")
    photo_ids: List[str] = Field(default=[], example=["photo-id-1", "photo-id-2"])

class GalleryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    pin: Optional[str] = Field(None, min_length=4, max_length=8)
    photo_ids: Optional[List[str]] = None

class GalleryResponse(BaseModel):
    id: str
    event_id: str
    event_name: Optional[str] = None
    name: str
    slug: str
    status: GalleryStatus
    published_at: Optional[str] = None
    created_by: str
    photo_count: int = 0
    created_at: str
    share_url: str

    class Config:
        from_attributes = True
