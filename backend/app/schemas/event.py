from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class EventCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, example="Annual Tech Summit 2026")
    description: Optional[str] = Field(None, example="Keynote & workshops photography event")
    event_date: date = Field(..., example="2026-09-20")

class EventUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    event_date: Optional[date] = None

class EventMemberAddRequest(BaseModel):
    user_id: str = Field(..., example="user-uuid-here")

class EventMemberResponse(BaseModel):
    id: str
    event_id: str
    user_id: str
    user_name: str
    user_email: str
    assigned_at: str

class EventResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    event_date: str
    created_by: str
    created_at: str
    photo_count: int = 0
    members: List[EventMemberResponse] = []

    class Config:
        from_attributes = True
