import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TEAM_MEMBER = "TEAM_MEMBER"

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="userrole_enum"),
        default=UserRole.TEAM_MEMBER,
        nullable=False
    )
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
    created_events = relationship("Event", back_populates="creator", cascade="all, delete-orphan")
    event_memberships = relationship("EventMember", back_populates="user", cascade="all, delete-orphan")
    uploaded_photos = relationship("Photo", back_populates="uploader", cascade="all, delete-orphan")
    created_galleries = relationship("Gallery", back_populates="creator", cascade="all, delete-orphan")
