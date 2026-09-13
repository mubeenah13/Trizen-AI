import secrets
import re
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.event import Event
from app.models.photo import Photo
from app.models.gallery import Gallery, GalleryStatus
from app.models.gallery_photo import GalleryPhoto
from app.core.security import hash_pin, verify_pin, create_gallery_access_token, decode_gallery_access_token
from app.schemas.gallery import GalleryCreateRequest, GalleryUpdateRequest, GalleryResponse
from app.schemas.public import PublicGalleryVerifyResponse, PublicGalleryMetaResponse, PublicPhotoResponse
from app.core.config import settings

def slugify(text: str) -> str:
    """Utility to convert gallery name to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

# In-memory brute-force protection tracker: slug -> (failed_attempts_count, lockout_until_timestamp)
_pin_attempt_tracker: Dict[str, Tuple[int, datetime]] = {}

class GalleryService:
    @staticmethod
    async def create_gallery(db: AsyncSession, req: GalleryCreateRequest, current_user: User) -> GalleryResponse:
        # Check event
        event_res = await db.execute(select(Event).where(Event.id == req.event_id))
        event = event_res.scalar_one_or_none()
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        
        # Verify ownership
        if current_user.role == UserRole.ADMIN and event.created_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this event")

        base_slug = slugify(req.name) or "gallery"
        unique_suffix = secrets.token_hex(3)
        slug = f"{base_slug}-{unique_suffix}"
        
        hashed_pin = hash_pin(req.pin)
        
        gallery = Gallery(
            event_id=req.event_id,
            name=req.name,
            slug=slug,
            pin_hash=hashed_pin,
            status=GalleryStatus.DRAFT,
            created_by=current_user.id
        )
        db.add(gallery)
        await db.commit()
        await db.refresh(gallery)
        
        if req.photo_ids:
            for photo_id in req.photo_ids:
                gp = GalleryPhoto(gallery_id=gallery.id, photo_id=photo_id)
                db.add(gp)
            await db.commit()
        
        return await GalleryService.get_gallery_by_id(db, gallery.id)

    @staticmethod
    async def get_gallery_by_id(db: AsyncSession, gallery_id: str) -> GalleryResponse:
        stmt = (
            select(Gallery)
            .where(Gallery.id == gallery_id)
            .options(
                selectinload(Gallery.event),
                selectinload(Gallery.gallery_photos)
            )
        )
        result = await db.execute(stmt)
        gallery = result.scalar_one_or_none()
        if not gallery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gallery not found")
        
        share_url = f"{settings.FRONTEND_URL}/gallery/{gallery.slug}"
        
        return GalleryResponse(
            id=gallery.id,
            event_id=gallery.event_id,
            event_name=gallery.event.name if gallery.event else None,
            name=gallery.name,
            slug=gallery.slug,
            status=gallery.status,
            published_at=gallery.published_at.isoformat() if gallery.published_at else None,
            created_by=gallery.created_by,
            photo_count=len(gallery.gallery_photos),
            created_at=gallery.created_at.isoformat(),
            share_url=share_url
        )

    @staticmethod
    async def update_gallery(
        db: AsyncSession,
        gallery_id: str,
        req: GalleryUpdateRequest,
        current_user: User
    ) -> GalleryResponse:
        stmt = select(Gallery).where(Gallery.id == gallery_id)
        res = await db.execute(stmt)
        gallery = res.scalar_one_or_none()
        if not gallery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gallery not found")
        
        if current_user.role == UserRole.ADMIN and gallery.created_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this gallery")

        if req.name:
            gallery.name = req.name
        if req.pin:
            gallery.pin_hash = hash_pin(req.pin)
        
        if req.photo_ids is not None:
            await db.execute(delete(GalleryPhoto).where(GalleryPhoto.gallery_id == gallery_id))
            for p_id in req.photo_ids:
                db.add(GalleryPhoto(gallery_id=gallery_id, photo_id=p_id))
        
        await db.commit()
        return await GalleryService.get_gallery_by_id(db, gallery_id)

    @staticmethod
    async def publish_gallery(db: AsyncSession, gallery_id: str, current_user: User) -> GalleryResponse:
        stmt = select(Gallery).where(Gallery.id == gallery_id)
        res = await db.execute(stmt)
        gallery = res.scalar_one_or_none()
        if not gallery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gallery not found")
        
        if current_user.role == UserRole.ADMIN and gallery.created_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this gallery")

        gallery.status = GalleryStatus.PUBLISHED
        gallery.published_at = datetime.now(timezone.utc)
        await db.commit()
        
        return await GalleryService.get_gallery_by_id(db, gallery_id)

    @staticmethod
    async def get_galleries_for_event(db: AsyncSession, event_id: str) -> List[GalleryResponse]:
        stmt = (
            select(Gallery)
            .where(Gallery.event_id == event_id)
            .options(
                selectinload(Gallery.event),
                selectinload(Gallery.gallery_photos)
            )
            .order_by(Gallery.created_at.desc())
        )
        res = await db.execute(stmt)
        galleries = res.scalars().all()
        
        responses = []
        for g in galleries:
            share_url = f"{settings.FRONTEND_URL}/gallery/{g.slug}"
            responses.append(
                GalleryResponse(
                    id=g.id,
                    event_id=g.event_id,
                    event_name=g.event.name if g.event else None,
                    name=g.name,
                    slug=g.slug,
                    status=g.status,
                    published_at=g.published_at.isoformat() if g.published_at else None,
                    created_by=g.created_by,
                    photo_count=len(g.gallery_photos),
                    created_at=g.created_at.isoformat(),
                    share_url=share_url
                )
            )
        return responses

    # --- PUBLIC CUSTOMER API METHODS WITH BRUTE-FORCE PROTECTION ---

    @staticmethod
    async def get_public_gallery_meta(db: AsyncSession, slug: str) -> PublicGalleryMetaResponse:
        stmt = (
            select(Gallery)
            .where(Gallery.slug == slug)
            .options(
                selectinload(Gallery.event),
                selectinload(Gallery.gallery_photos)
            )
        )
        res = await db.execute(stmt)
        gallery = res.scalar_one_or_none()
        
        if not gallery or gallery.status != GalleryStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallery not found or is currently private/unpublished."
            )
        
        return PublicGalleryMetaResponse(
            name=gallery.name,
            slug=gallery.slug,
            event_name=gallery.event.name if gallery.event else "Event",
            event_date=gallery.event.event_date.isoformat() if gallery.event else "",
            photo_count=len(gallery.gallery_photos),
            is_protected=True
        )

    @staticmethod
    async def verify_pin_and_issue_token(db: AsyncSession, slug: str, pin: str) -> PublicGalleryVerifyResponse:
        now = datetime.now(timezone.utc)
        
        # Check Brute Force Lockout
        if slug in _pin_attempt_tracker:
            attempts, lockout_until = _pin_attempt_tracker[slug]
            if now < lockout_until:
                remaining_sec = int((lockout_until - now).total_seconds())
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many incorrect PIN attempts. Locked out for {remaining_sec} seconds."
                )

        stmt = (
            select(Gallery)
            .where(Gallery.slug == slug)
            .options(
                selectinload(Gallery.event),
                selectinload(Gallery.gallery_photos)
            )
        )
        res = await db.execute(stmt)
        gallery = res.scalar_one_or_none()
        
        if not gallery or gallery.status != GalleryStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallery not found or is not published."
            )
        
        if not verify_pin(pin, gallery.pin_hash):
            attempts, lockout_until = _pin_attempt_tracker.get(slug, (0, now))
            new_attempts = attempts + 1
            if new_attempts >= settings.MAX_PIN_ATTEMPTS:
                new_lockout = now + timedelta(minutes=settings.PIN_LOCKOUT_MINUTES)
                _pin_attempt_tracker[slug] = (new_attempts, new_lockout)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Maximum PIN verification attempts exceeded. Gallery locked for {settings.PIN_LOCKOUT_MINUTES} minutes."
                )
            else:
                _pin_attempt_tracker[slug] = (new_attempts, now)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Incorrect gallery PIN. ({settings.MAX_PIN_ATTEMPTS - new_attempts} attempts remaining)"
                )
        
        # Successful PIN verification -> Reset counter
        if slug in _pin_attempt_tracker:
            del _pin_attempt_tracker[slug]
        
        access_token = create_gallery_access_token(gallery_id=gallery.id, slug=gallery.slug)
        
        return PublicGalleryVerifyResponse(
            gallery_access_token=access_token,
            token_type="bearer",
            gallery_name=gallery.name,
            event_name=gallery.event.name if gallery.event else "Event",
            photo_count=len(gallery.gallery_photos)
        )

    @staticmethod
    async def get_public_gallery_photos(
        db: AsyncSession,
        slug: str,
        token_payload: dict,
        raw_token: str = ""
    ) -> List[PublicPhotoResponse]:
        stmt = (
            select(Gallery)
            .where(Gallery.slug == slug)
            .options(selectinload(Gallery.gallery_photos).selectinload(GalleryPhoto.photo))
        )
        res = await db.execute(stmt)
        gallery = res.scalar_one_or_none()
        
        if not gallery or gallery.status != GalleryStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gallery not found or is not published."
            )
        
        # Token gallery-scoped match verification
        if token_payload.get("gallery_id") != gallery.id or token_payload.get("slug") != slug:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Your gallery security token is for a different gallery."
            )
        
        photos = []
        for gp in gallery.gallery_photos:
            p = gp.photo
            if p:
                photo_url = f"/api/v1/public/galleries/stream/{p.id}?token={raw_token}"
                photos.append(
                    PublicPhotoResponse(
                        id=p.id,
                        filename=p.filename,
                        file_size=p.file_size,
                        mime_type=p.mime_type,
                        url=photo_url,
                        created_at=p.created_at.isoformat()
                    )
                )
        return photos
