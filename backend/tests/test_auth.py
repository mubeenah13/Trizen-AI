import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_user_registration(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "New Photographer",
            "email": "newphoto@trizen.ai",
            "password": "Password123!",
            "role": "TEAM_MEMBER"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newphoto@trizen.ai"
    assert data["user"]["role"] == "TEAM_MEMBER"

@pytest.mark.asyncio
async def test_user_login(client: AsyncClient, admin_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "testadmin@trizen.ai",
            "password": "AdminPass123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "testadmin@trizen.ai"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, admin_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "testadmin@trizen.ai",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_auth_me(client: AsyncClient, admin_headers):
    response = await client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testadmin@trizen.ai"
    assert data["role"] == "ADMIN"
