import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.event_member import EventMember

TEST_DB_URL = "sqlite+aiosqlite:///./test_trizen_photos.db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def test_db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    TestingSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    if os.path.exists("./test_trizen_photos.db"):
        os.remove("./test_trizen_photos.db")

@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession):
    async def _get_test_db():
        yield test_db

    app.dependency_overrides[get_db] = _get_test_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def admin_user(test_db: AsyncSession) -> User:
    admin = User(
        name="Test Admin",
        email="testadmin@trizen.ai",
        password_hash=get_password_hash("AdminPass123!"),
        role=UserRole.ADMIN
    )
    test_db.add(admin)
    await test_db.commit()
    await test_db.refresh(admin)
    return admin

@pytest_asyncio.fixture(scope="function")
async def admin_headers(admin_user: User) -> dict:
    token = create_access_token(subject=admin_user.id, role=admin_user.role.value)
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture(scope="function")
async def team_user(test_db: AsyncSession) -> User:
    team = User(
        name="Test Team Member",
        email="testteam@trizen.ai",
        password_hash=get_password_hash("TeamPass123!"),
        role=UserRole.TEAM_MEMBER
    )
    test_db.add(team)
    await test_db.commit()
    await test_db.refresh(team)
    return team

@pytest_asyncio.fixture(scope="function")
async def team_headers(team_user: User) -> dict:
    token = create_access_token(subject=team_user.id, role=team_user.role.value)
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture(scope="function")
async def unassigned_team_user(test_db: AsyncSession) -> User:
    team2 = User(
        name="Unassigned Team Member",
        email="unassigned@trizen.ai",
        password_hash=get_password_hash("TeamPass123!"),
        role=UserRole.TEAM_MEMBER
    )
    test_db.add(team2)
    await test_db.commit()
    await test_db.refresh(team2)
    return team2

@pytest_asyncio.fixture(scope="function")
async def unassigned_headers(unassigned_team_user: User) -> dict:
    token = create_access_token(subject=unassigned_team_user.id, role=unassigned_team_user.role.value)
    return {"Authorization": f"Bearer {token}"}
