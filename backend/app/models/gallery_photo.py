import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class GalleryPhoto(Base):
    __tablename__ = "gallery_photos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gallery_id: Mapped[str] = mapped_column(String(36), ForeignKey("galleries.id", ondelete="CASCADE"), nullable=False, index=True)
    photo_id: Mapped[str] = mapped_column(String(36), ForeignKey("photos.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("gallery_id", "photo_id", name="uq_gallery_photo"),
    )

    # Relationships
    gallery = relationship("Gallery", back_populates="gallery_photos")
    photo = relationship("Photo", back_populates="gallery_associations")
