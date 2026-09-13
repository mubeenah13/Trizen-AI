from typing import List, Optional
from fastapi import APIRouter, Depends, status, Response, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_gallery_token_payload
from app.schemas.public import PublicGalleryVerifyRequest, PublicGalleryVerifyResponse, PublicGalleryMetaResponse, PublicPhotoResponse
from app.services.gallery_service import GalleryService
from app.models.gallery import Gallery, GalleryStatus
from app.models.gallery_photo import GalleryPhoto
from app.models.photo import Photo
from app.services.storage_service import storage_service

router = APIRouter(prefix="/public/galleries", tags=["Public Customer Gallery"])

@router.get("/{slug}", response_model=PublicGalleryMetaResponse)
async def get_public_gallery_meta(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Public Endpoint: Get basic gallery title and photo count for PIN challenge screen.
    Unpublished/Draft galleries return 404.
    """
    return await GalleryService.get_public_gallery_meta(db, slug)

@router.post("/{slug}/verify", response_model=PublicGalleryVerifyResponse)
async def verify_gallery_pin(
    slug: str,
    req: PublicGalleryVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Public Endpoint: Verify 4-8 digit PIN against stored bcrypt hash.
    On success, returns short-lived signed JWT gallery_access_token.
    """
    return await GalleryService.verify_pin_and_issue_token(db, slug, req.pin)

@router.get("/{slug}/photos", response_model=List[PublicPhotoResponse])
async def get_public_gallery_photos(
    slug: str,
    db: AsyncSession = Depends(get_db),
    token_payload: dict = Depends(get_gallery_token_payload),
    x_gallery_token: Optional[str] = Header(None, alias="X-Gallery-Token"),
    token: Optional[str] = Query(None)
):
    """
    Public Endpoint: Get published photos after valid PIN verification.
    Requires X-Gallery-Token header. Returns ONLY photos in gallery_photos.
    Unpublished photos or arbitrary event photos are strictly blocked.
    """
    raw_token = x_gallery_token or token or ""
    return await GalleryService.get_public_gallery_photos(db, slug, token_payload, raw_token=raw_token)

@router.get("/stream/{photo_id}")
async def stream_public_gallery_photo(
    photo_id: str,
    token: Optional[str] = Query(None),
    x_gallery_token: Optional[str] = Header(None, alias="X-Gallery-Token"),
    db: AsyncSession = Depends(get_db)
):
    """
    Public Proxy Image Stream: Streams image file ONLY if photo belongs to a published gallery
    and a valid gallery access token is provided.
    """
    gallery_token = token or x_gallery_token
    if not gallery_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Gallery token required to view photo")
    
    # Verify gallery token
    from app.core.security import decode_gallery_access_token
    payload = decode_gallery_access_token(gallery_token)
    gallery_id = payload.get("gallery_id")
    
    # Check if photo is in this gallery
    stmt = (
        select(GalleryPhoto)
        .join(Gallery, GalleryPhoto.gallery_id == Gallery.id)
        .where(
            GalleryPhoto.gallery_id == gallery_id,
            GalleryPhoto.photo_id == photo_id,
            Gallery.status == GalleryStatus.PUBLISHED
        )
    )
    res = await db.execute(stmt)
    assoc = res.scalar_one_or_none()
    if not assoc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied. This photo is not part of your unlocked published gallery."
        )
    
    photo_res = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = photo_res.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    
    file_bytes = storage_service.get_file_bytes(photo.storage_key)
    return Response(content=file_bytes, media_type=photo.mime_type)
