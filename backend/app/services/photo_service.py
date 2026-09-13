from typing import List, Optional
import io
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole
from app.models.event import Event
from app.models.photo import Photo
from app.schemas.photo import PhotoResponse
from app.services.storage_service import storage_service

ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif", "image/heic"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB limit per file

class PhotoService:
    @staticmethod
    async def upload_photos(
        db: AsyncSession,
        event_id: str,
        files: List[UploadFile],
        current_user: User
    ) -> List[PhotoResponse]:
        """
        Uploads multiple photos for an event.
        Includes server-side file validation, storage key creation, object storage upload,
        and database metadata insertion with automatic rollback and orphan object cleanup on error.
        """
        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No photo files uploaded")
        
        uploaded_keys: List[str] = []
        created_photos: List[Photo] = []
        
        try:
            for file in files:
                # 1. Content type & size validation
                content_type = file.content_type.lower() if file.content_type else ""
                if content_type not in ALLOWED_MIME_TYPES:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unsupported file format '{file.filename}'. Allowed: JPG, PNG, WEBP, GIF, HEIC."
                    )
                
                file_bytes = await file.read()
                if len(file_bytes) > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File '{file.filename}' exceeds maximum allowed size of 25MB."
                    )
                
                # Image dimensions inspection
                width, height = None, None
                try:
                    with Image.open(io.BytesIO(file_bytes)) as img:
                        width, height = img.size
                except Exception:
                    pass  # Non-critical metadata
                
                # 2. Upload to S3/MinIO
                storage_meta = storage_service.upload_file(
                    file_bytes=file_bytes,
                    filename=file.filename,
                    content_type=content_type,
                    event_id=event_id
                )
                uploaded_keys.append(storage_meta["storage_key"])
                
                # 3. Create Photo DB record
                photo = Photo(
                    event_id=event_id,
                    uploaded_by=current_user.id,
                    filename=file.filename,
                    storage_key=storage_meta["storage_key"],
                    storage_url=storage_meta["storage_url"],
                    file_size=storage_meta["file_size"],
                    mime_type=content_type,
                    width=width,
                    height=height
                )
                db.add(photo)
                created_photos.append(photo)
            
            await db.commit()
            
            # Refresh to get IDs
            responses = []
            for p in created_photos:
                await db.refresh(p)
                url = f"/api/v1/photos/stream/{p.id}"
                responses.append(
                    PhotoResponse(
                        id=p.id,
                        event_id=p.event_id,
                        uploaded_by=p.uploaded_by,
                        uploader_name=current_user.name,
                        filename=p.filename,
                        storage_key=p.storage_key,
                        url=url,
                        file_size=p.file_size,
                        mime_type=p.mime_type,
                        width=p.width,
                        height=p.height,
                        created_at=p.created_at.isoformat()
                    )
                )
            
            return responses

        except Exception as e:
            # Failure Rollback & Orphan Object Cleanup
            await db.rollback()
            for key in uploaded_keys:
                storage_service.delete_file(key)
            
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process photo upload: {str(e)}"
            )

    @staticmethod
    async def get_event_photos(
        db: AsyncSession,
        event_id: str,
        current_user: User,
        only_mine: bool = False
    ) -> List[PhotoResponse]:
        """
        Retrieves photos for an event with uploader info.
        Admin sees all photos. Team Member sees event photos or only their own depending on permission.
        """
        stmt = (
            select(Photo)
            .where(Photo.event_id == event_id)
            .options(selectinload(Photo.uploader))
            .order_by(Photo.created_at.desc())
        )
        
        if only_mine or (current_user.role == UserRole.TEAM_MEMBER and only_mine):
            stmt = stmt.where(Photo.uploaded_by == current_user.id)
            
        result = await db.execute(stmt)
        photos = result.scalars().all()
        
        responses = []
        for p in photos:
            url = f"/api/v1/photos/stream/{p.id}"
            responses.append(
                PhotoResponse(
                    id=p.id,
                    event_id=p.event_id,
                    uploaded_by=p.uploaded_by,
                    uploader_name=p.uploader.name if p.uploader else "Unknown",
                    filename=p.filename,
                    storage_key=p.storage_key,
                    url=url,
                    file_size=p.file_size,
                    mime_type=p.mime_type,
                    width=p.width,
                    height=p.height,
                    created_at=p.created_at.isoformat()
                )
            )
        return responses

    @staticmethod
    async def delete_photo(db: AsyncSession, photo_id: str, current_user: User):
        result = await db.execute(select(Photo).where(Photo.id == photo_id))
        photo = result.scalar_one_or_none()
        if not photo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
        
        # Check permissions: Admin or photo uploader
        if current_user.role != UserRole.ADMIN and photo.uploaded_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this photo")
        
        storage_service.delete_file(photo.storage_key)
        await db.delete(photo)
        await db.commit()
