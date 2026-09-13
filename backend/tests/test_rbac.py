import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_create_event(client: AsyncClient, admin_headers):
    response = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={
            "name": "Summer Concert 2026",
            "description": "Live music event photos",
            "event_date": "2026-07-15"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Summer Concert 2026"

@pytest.mark.asyncio
async def test_team_member_cannot_create_gallery(client: AsyncClient, team_headers, admin_headers):
    # Admin creates event
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "Corporate Retreat", "event_date": "2026-08-01"}
    )
    event_id = ev_res.json()["id"]

    # Team member attempts gallery creation -> 403 Forbidden
    response = await client.post(
        "/api/v1/galleries",
        headers=team_headers,
        json={
            "event_id": event_id,
            "name": "Unauthorized Gallery",
            "pin": "123456"
        }
    )
    assert response.status_code == 403
    assert "Required role: ADMIN" in response.json()["detail"]

@pytest.mark.asyncio
async def test_unassigned_team_member_blocked_from_event(
    client: AsyncClient,
    admin_headers,
    unassigned_headers
):
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "VIP Fashion Show", "event_date": "2026-09-01"}
    )
    event_id = ev_res.json()["id"]

    # Unassigned team member attempts event access -> 403
    response = await client.get(f"/api/v1/events/{event_id}", headers=unassigned_headers)
    assert response.status_code == 403
    assert "not assigned to this event" in response.json()["detail"]
