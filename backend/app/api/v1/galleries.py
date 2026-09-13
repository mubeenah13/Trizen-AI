from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import require_admin, require_any_user, verify_event_access
from app.models.user import User, UserRole
from app.schemas.gallery import GalleryCreateRequest, GalleryUpdateRequest, GalleryResponse
from app.services.gallery_service import GalleryService

router = APIRouter(prefix="/galleries", tags=["Galleries"])

@router.post("", response_model=GalleryResponse, status_code=status.HTTP_201_CREATED)
async def create_gallery(
    req: GalleryCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Admin only: Create a new customer gallery."""
    return await GalleryService.create_gallery(db, req, admin_user)

@router.get("/{gallery_id}", response_model=GalleryResponse)
async def get_gallery(
    gallery_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Admin only: Get details of a gallery."""
    return await GalleryService.get_gallery_by_id(db, gallery_id)

@router.put("/{gallery_id}", response_model=GalleryResponse)
async def update_gallery(
    gallery_id: str,
    req: GalleryUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Admin only: Update gallery details or selected photos."""
    return await GalleryService.update_gallery(db, gallery_id, req, admin_user)

@router.post("/{gallery_id}/publish", response_model=GalleryResponse)
async def publish_gallery(
    gallery_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Admin only: Publish the gallery, making it accessible to customers via PIN.
    Team members trying to publish receive an explicit HTTP 403 Forbidden.
    """
    return await GalleryService.publish_gallery(db, gallery_id, admin_user)

@router.get("/events/{event_id}", response_model=List[GalleryResponse])
async def list_event_galleries(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Admin only: List galleries created for an event."""
    return await GalleryService.get_galleries_for_event(db, event_id)
