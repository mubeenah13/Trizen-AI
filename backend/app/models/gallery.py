import enum
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class GalleryStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"

class Gallery(Base):
    __tablename__ = "galleries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    pin_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[GalleryStatus] = mapped_column(
        SQLEnum(GalleryStatus, name="gallerystatus_enum"),
        default=GalleryStatus.DRAFT,
        nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    event = relationship("Event", back_populates="galleries")
    creator = relationship("User", back_populates="created_galleries")
    gallery_photos = relationship("GalleryPhoto", back_populates="gallery", cascade="all, delete-orphan")
