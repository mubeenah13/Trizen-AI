import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_create_event(client: AsyncClient, admin_headers):
    response = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={
            "name": "Summer Fashion Show 2026",
            "description": "Runway and backstage photography",
            "event_date": "2026-08-15"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Summer Fashion Show 2026"
    assert data["photo_count"] == 0

@pytest.mark.asyncio
async def test_admin_assign_team_member(client: AsyncClient, admin_headers, team_user):
    # 1. Create event
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "Tech Expo 2026", "event_date": "2026-09-01"}
    )
    event_id = ev_res.json()["id"]

    # 2. Assign team member
    assign_res = await client.post(
        f"/api/v1/events/{event_id}/members",
        headers=admin_headers,
        json={"user_id": team_user.id}
    )
    assert assign_res.status_code == 201
    data = assign_res.json()
    assert data["user_id"] == team_user.id

@pytest.mark.asyncio
async def test_team_member_can_access_assigned_event(client: AsyncClient, admin_headers, team_headers, team_user):
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "Charity Gala", "event_date": "2026-10-05"}
    )
    event_id = ev_res.json()["id"]

    await client.post(
        f"/api/v1/events/{event_id}/members",
        headers=admin_headers,
        json={"user_id": team_user.id}
    )

    response = await client.get(f"/api/v1/events/{event_id}", headers=team_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Charity Gala"

@pytest.mark.asyncio
async def test_team_member_cannot_access_unassigned_event(client: AsyncClient, admin_headers, unassigned_headers):
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "Private VIP Dinner", "event_date": "2026-11-12"}
    )
    event_id = ev_res.json()["id"]

    response = await client.get(f"/api/v1/events/{event_id}", headers=unassigned_headers)
    assert response.status_code == 403
    assert "not assigned to this event" in response.json()["detail"]
