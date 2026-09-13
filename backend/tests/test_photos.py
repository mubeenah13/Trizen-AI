import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_team_member_can_upload_photo(client: AsyncClient, admin_headers, team_headers, team_user):
    # 1. Create event & assign team member
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "Concert 2026", "event_date": "2026-06-20"}
    )
    event_id = ev_res.json()["id"]

    await client.post(
        f"/api/v1/events/{event_id}/members",
        headers=admin_headers,
        json={"user_id": team_user.id}
    )

    # 2. Upload valid photo file
    dummy_jpg = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444'9=82<.342\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xFF\xDA\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xFF\xD9"
    files = [("files", ("stage_light.jpg", dummy_jpg, "image/jpeg"))]

    up_res = await client.post(
        f"/api/v1/events/{event_id}/photos",
        headers=team_headers,
        files=files
    )
    assert up_res.status_code == 201
    photos = up_res.json()
    assert len(photos) == 1
    assert photos[0]["filename"] == "stage_light.jpg"

@pytest.mark.asyncio
async def test_invalid_file_upload(client: AsyncClient, admin_headers, team_headers, team_user):
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "Conference 2026", "event_date": "2026-07-01"}
    )
    event_id = ev_res.json()["id"]

    await client.post(
        f"/api/v1/events/{event_id}/members",
        headers=admin_headers,
        json={"user_id": team_user.id}
    )

    # Unsupported format (PDF)
    files = [("files", ("document.pdf", b"%PDF-1.4...", "application/pdf"))]
    response = await client.post(
        f"/api/v1/events/{event_id}/photos",
        headers=team_headers,
        files=files
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

@pytest.mark.asyncio
async def test_team_member_cannot_access_unassigned_event_photos(client: AsyncClient, admin_headers, unassigned_headers):
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "Secret Keynote", "event_date": "2026-09-10"}
    )
    event_id = ev_res.json()["id"]

    response = await client.get(f"/api/v1/events/{event_id}/photos", headers=unassigned_headers)
    assert response.status_code == 403
