from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, require_admin, require_any_user, verify_event_access
from app.models.user import User, UserRole
from app.models.event import Event
from app.schemas.event import EventCreateRequest, EventUpdateRequest, EventResponse, EventMemberAddRequest, EventMemberResponse
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    req: EventCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Admin only: Create a new event."""
    return await EventService.create_event(db, req, admin_user)

@router.get("", response_model=List[EventResponse])
async def list_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_user)
):
    """
    List events accessible to user.
    - Admin sees all events.
    - Team Member sees only assigned events.
    """
    return await EventService.get_events_for_user(db, current_user)

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    event: Event = Depends(verify_event_access)
):
    """Get single event details if user has permission to access it."""
    return await EventService.get_event_by_id(db, event_id)

@router.post("/{event_id}/members", response_model=EventMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_event_member(
    event_id: str,
    req: EventMemberAddRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Admin only: Assign a team member to an event."""
    return await EventService.add_member_to_event(db, event_id, req.user_id)

@router.delete("/{event_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_event_member(
    event_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Admin only: Remove a team member assignment from an event."""
    await EventService.remove_member_from_event(db, event_id, user_id)
