import asyncio
from datetime import date, datetime, timezone
from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.event_member import EventMember
from app.models.photo import Photo
from app.models.gallery import Gallery, GalleryStatus
from app.models.gallery_photo import GalleryPhoto
from app.core.security import get_password_hash, hash_pin
from app.services.storage_service import storage_service
import app.models

async def seed_data():
    print("=== [SEED] Initializing Database Tables & Demo Data ===")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Admin User
        admin_res = await db.execute(select(User).where(User.email == "admin@trizen.ai"))
        admin = admin_res.scalar_one_or_none()
        if not admin:
            admin = User(
                name="Sarah Admin (Lead)",
                email="admin@trizen.ai",
                password_hash=get_password_hash("Admin123!"),
                role=UserRole.ADMIN
            )
            db.add(admin)
            await db.flush()
            print("  [+] Created Admin account: admin@trizen.ai / Admin123!")
        
        # 2. Team Member User
        team_res = await db.execute(select(User).where(User.email == "team@trizen.ai"))
        team_member = team_res.scalar_one_or_none()
        if not team_member:
            team_member = User(
                name="Alex Photographer",
                email="team@trizen.ai",
                password_hash=get_password_hash("Team123!"),
                role=UserRole.TEAM_MEMBER
            )
            db.add(team_member)
            await db.flush()
            print("  [+] Created Team Member account: team@trizen.ai / Team123!")

        # 3. Demo Event
        event_res = await db.execute(select(Event).where(Event.name == "TrizenAI Annual Tech Gala 2026"))
        event = event_res.scalar_one_or_none()
        if not event:
            event = Event(
                name="TrizenAI Annual Tech Gala 2026",
                description="Official company gala, keynote awards, and team celebrations.",
                event_date=date(2026, 9, 20),
                created_by=admin.id
            )
            db.add(event)
            await db.flush()
            print("  [+] Created Demo Event: TrizenAI Annual Tech Gala 2026")
        
        # 4. Assign Team Member to Event
        em_res = await db.execute(
            select(EventMember).where(EventMember.event_id == event.id, EventMember.user_id == team_member.id)
        )
        if not em_res.scalar_one_or_none():
            em = EventMember(event_id=event.id, user_id=team_member.id)
            db.add(em)
            await db.flush()
            print("  [+] Assigned Alex Photographer to TrizenAI Annual Tech Gala 2026")

        # 5. Create Sample Photos (SVG/PNG Placeholders in Storage)
        photo_ids = []
        existing_photos_res = await db.execute(select(Photo).where(Photo.event_id == event.id))
        existing_photos = existing_photos_res.scalars().all()
        
        if not existing_photos:
            sample_photos_data = [
                ("Keynote_Address.jpg", 1920, 1080),
                ("Team_Award_Ceremony.jpg", 1920, 1200),
                ("Executive_Toast.jpg", 1920, 1080),
                ("Networking_Lounge.jpg", 1920, 1080),
            ]
            
            for filename, w, h in sample_photos_data:
                # Generate simple placeholder bytes
                dummy_svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="100%" height="100%" fill="#1e293b"/><text x="50%" y="50%" fill="#38bdf8" font-size="48" text-anchor="middle" font-family="sans-serif">{filename}</text></svg>'
                file_bytes = dummy_svg.encode("utf-8")
                
                meta = storage_service.upload_file(
                    file_bytes=file_bytes,
                    filename=filename,
                    content_type="image/svg+xml",
                    event_id=event.id
                )
                
                photo = Photo(
                    event_id=event.id,
                    uploaded_by=team_member.id,
                    filename=filename,
                    storage_key=meta["storage_key"],
                    storage_url=meta["storage_url"],
                    file_size=meta["file_size"],
                    mime_type="image/svg+xml",
                    width=w,
                    height=h
                )
                db.add(photo)
                await db.flush()
                photo_ids.append(photo.id)
                print(f"  [+] Created Sample Photo: {filename}")
        else:
            photo_ids = [p.id for p in existing_photos]

        # 6. Create Demo Published Gallery
        gal_res = await db.execute(select(Gallery).where(Gallery.slug == "gala-highlights-2026"))
        gallery = gal_res.scalar_one_or_none()
        if not gallery:
            gallery = Gallery(
                event_id=event.id,
                name="Gala Official Highlights",
                slug="gala-highlights-2026",
                pin_hash=hash_pin("123456"),
                status=GalleryStatus.PUBLISHED,
                published_at=datetime.now(timezone.utc),
                created_by=admin.id
            )
            db.add(gallery)
            await db.flush()
            
            for pid in photo_ids:
                gp = GalleryPhoto(gallery_id=gallery.id, photo_id=pid)
                db.add(gp)
            print("  [+] Created Demo Published Gallery: Gala Official Highlights (Slug: gala-highlights-2026, PIN: 123456)")

        await db.commit()
        print("=== [SEED] Seeding Completed Successfully! ===")

if __name__ == "__main__":
    asyncio.run(seed_data())
