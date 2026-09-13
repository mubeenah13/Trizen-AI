from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.event_member import EventMember
from app.models.photo import Photo
from app.schemas.event import EventCreateRequest, EventUpdateRequest, EventResponse, EventMemberResponse

class EventService:
    @staticmethod
    async def create_event(db: AsyncSession, req: EventCreateRequest, current_user: User) -> EventResponse:
        new_event = Event(
            name=req.name,
            description=req.description,
            event_date=req.event_date,
            created_by=current_user.id
        )
        db.add(new_event)
        await db.commit()
        await db.refresh(new_event)
        return await EventService.get_event_by_id(db, new_event.id)

    @staticmethod
    async def get_events_for_user(db: AsyncSession, current_user: User) -> List[EventResponse]:
        if current_user.role == UserRole.ADMIN:
            stmt = select(Event).options(selectinload(Event.members).selectinload(EventMember.user)).order_by(Event.created_at.desc())
        else:
            # Team Member: Filter only assigned events
            stmt = (
                select(Event)
                .join(EventMember, Event.id == EventMember.event_id)
                .where(EventMember.user_id == current_user.id)
                .options(selectinload(Event.members).selectinload(EventMember.user))
                .order_by(Event.created_at.desc())
            )
        
        result = await db.execute(stmt)
        events = result.scalars().all()
        
        event_responses = []
        for event in events:
            # Count photos
            photo_count_res = await db.execute(select(func.count(Photo.id)).where(Photo.event_id == event.id))
            photo_count = photo_count_res.scalar() or 0
            
            members_list = [
                EventMemberResponse(
                    id=m.id,
                    event_id=m.event_id,
                    user_id=m.user_id,
                    user_name=m.user.name if m.user else "Unknown",
                    user_email=m.user.email if m.user else "Unknown",
                    assigned_at=m.assigned_at.isoformat()
                )
                for m in event.members
            ]
            
            event_responses.append(
                EventResponse(
                    id=event.id,
                    name=event.name,
                    description=event.description,
                    event_date=event.event_date.isoformat(),
                    created_by=event.created_by,
                    created_at=event.created_at.isoformat(),
                    photo_count=photo_count,
                    members=members_list
                )
            )
        
        return event_responses

    @staticmethod
    async def get_event_by_id(db: AsyncSession, event_id: str) -> EventResponse:
        stmt = select(Event).where(Event.id == event_id).options(selectinload(Event.members).selectinload(EventMember.user))
        result = await db.execute(stmt)
        event = result.scalar_one_or_none()
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
        
        photo_count_res = await db.execute(select(func.count(Photo.id)).where(Photo.event_id == event_id))
        photo_count = photo_count_res.scalar() or 0
        
        members_list = [
            EventMemberResponse(
                id=m.id,
                event_id=m.event_id,
                user_id=m.user_id,
                user_name=m.user.name if m.user else "Unknown",
                user_email=m.user.email if m.user else "Unknown",
                assigned_at=m.assigned_at.isoformat()
            )
            for m in event.members
        ]
        
        return EventResponse(
            id=event.id,
            name=event.name,
            description=event.description,
            event_date=event.event_date.isoformat(),
            created_by=event.created_by,
            created_at=event.created_at.isoformat(),
            photo_count=photo_count,
            members=members_list
        )

    @staticmethod
    async def add_member_to_event(db: AsyncSession, event_id: str, user_id: str) -> EventMemberResponse:
        # Check target user
        user_res = await db.execute(select(User).where(User.id == user_id))
        user = user_res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target team member user not found")
        
        # Check duplicate assignment
        existing = await db.execute(
            select(EventMember).where(EventMember.event_id == event_id, EventMember.user_id == user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already assigned to this event")
        
        member = EventMember(event_id=event_id, user_id=user_id)
        db.add(member)
        await db.commit()
        await db.refresh(member)
        
        return EventMemberResponse(
            id=member.id,
            event_id=member.event_id,
            user_id=member.user_id,
            user_name=user.name,
            user_email=user.email,
            assigned_at=member.assigned_at.isoformat()
        )

    @staticmethod
    async def remove_member_from_event(db: AsyncSession, event_id: str, user_id: str):
        result = await db.execute(
            select(EventMember).where(EventMember.event_id == event_id, EventMember.user_id == user_id)
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member assignment not found")
        
        await db.delete(member)
        await db.commit()
