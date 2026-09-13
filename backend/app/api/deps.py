from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_access_token, decode_gallery_access_token
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.event_member import EventMember

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency verifying user JWT token and returning authenticated User database model."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token payload",
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists",
        )
    
    return user

class RequireRole:
    """Dependency class enforcing server-side Role-Based Access Control (RBAC)."""
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join([r.value for r in self.allowed_roles])}"
            )
        return current_user

require_admin = RequireRole([UserRole.ADMIN])
require_any_user = RequireRole([UserRole.ADMIN, UserRole.TEAM_MEMBER])

async def verify_event_access(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Event:
    """
    Verifies that the current user is authorized to access the specified event.
    - ADMIN: Must be creator of the event (or assigned as a member) to manage it.
    - TEAM_MEMBER: Can only access events to which they are explicitly assigned in event_members.
    """
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    if current_user.role == UserRole.ADMIN:
        if event.created_by == current_user.id:
            return event
        
        # Check if Admin is assigned as a member
        member_res = await db.execute(
            select(EventMember).where(
                EventMember.event_id == event_id,
                EventMember.user_id == current_user.id
            )
        )
        if member_res.scalar_one_or_none():
            return event

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not own or have permission to manage this event."
        )
    
    # Team Member check
    member_result = await db.execute(
        select(EventMember).where(
            EventMember.event_id == event_id,
            EventMember.user_id == current_user.id
        )
    )
    is_assigned = member_result.scalar_one_or_none()
    if not is_assigned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You are not assigned to this event."
        )
    
    return event

async def get_gallery_token_payload(
    x_gallery_token: Optional[str] = Header(None, alias="X-Gallery-Token"),
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Extracts and decodes customer gallery token from 'X-Gallery-Token' header or 'Bearer' authorization header.
    """
    token = x_gallery_token
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gallery access token required. Please enter gallery PIN."
        )
    
    return decode_gallery_access_token(token)
