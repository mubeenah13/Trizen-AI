from typing import List, Optional
from fastapi import APIRouter, Depends, status, UploadFile, File, Response, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user, require_any_user, verify_event_access
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.photo import Photo
from app.schemas.photo import PhotoResponse
from app.services.photo_service import PhotoService
from app.services.storage_service import storage_service

router = APIRouter(prefix="", tags=["Photos"])

@router.post("/events/{event_id}/photos", response_model=List[PhotoResponse], status_code=status.HTTP_201_CREATED)
async def upload_photos(
    event_id: str,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_user),
    event: Event = Depends(verify_event_access)
):
    """
    Upload multiple photos for an event.
    Team members can upload photos to events they are assigned to.
    """
    return await PhotoService.upload_photos(db, event_id, files, current_user)

@router.get("/events/{event_id}/photos", response_model=List[PhotoResponse])
async def get_event_photos(
    event_id: str,
    only_mine: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_user),
    event: Event = Depends(verify_event_access)
):
    """List photos in an event with server-side authorization filter."""
    return await PhotoService.get_event_photos(db, event_id, current_user, only_mine=only_mine)

@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_user)
):
    """Delete photo by photo ID (Admin or Photo Uploader only)."""
    await PhotoService.delete_photo(db, photo_id, current_user)

@router.get("/photos/stream/{photo_id}")
async def stream_photo(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Proxy image stream for authenticated users.
    Verifies user has access to the event containing this photo.
    """
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    
    # Check event access
    await verify_event_access(photo.event_id, current_user, db)
    
    file_bytes = storage_service.get_file_bytes(photo.storage_key)
    return Response(content=file_bytes, media_type=photo.mime_type)

@router.get("/photos/local-stream/{file_key}")
async def stream_local_photo(file_key: str):
    """Fallback handler for local storage mode."""
    storage_key = file_key.replace("_", "/")
    file_bytes = storage_service.get_file_bytes(storage_key)
    return Response(content=file_bytes, media_type="image/jpeg")
