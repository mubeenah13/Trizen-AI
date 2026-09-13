import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_create_select_and_publish_gallery(client: AsyncClient, admin_headers, team_headers, team_user):
    # 1. Create event & upload photo
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "Awards Night 2026", "event_date": "2026-11-20"}
    )
    event_id = ev_res.json()["id"]

    await client.post(
        f"/api/v1/events/{event_id}/members",
        headers=admin_headers,
        json={"user_id": team_user.id}
    )

    dummy_jpg = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444'9=82<.342\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xFF\xDA\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xFF\xD9"
    files = [("files", ("winner_trophy.jpg", dummy_jpg, "image/jpeg"))]
    up_res = await client.post(f"/api/v1/events/{event_id}/photos", headers=team_headers, files=files)
    photo_id = up_res.json()[0]["id"]

    # 2. Admin creates gallery
    gal_res = await client.post(
        "/api/v1/galleries",
        headers=admin_headers,
        json={
            "event_id": event_id,
            "name": "Official Awards Gallery",
            "pin": "555666",
            "photo_ids": [photo_id]
        }
    )
    assert gal_res.status_code == 201
    gallery = gal_res.json()
    assert gallery["status"] == "DRAFT"
    assert gallery["photo_count"] == 1

    # 3. Admin publishes gallery
    pub_res = await client.post(f"/api/v1/galleries/{gallery['id']}/publish", headers=admin_headers)
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "PUBLISHED"

@pytest.mark.asyncio
async def test_team_member_cannot_publish_gallery(client: AsyncClient, admin_headers, team_headers):
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "Summit 2026", "event_date": "2026-12-01"}
    )
    event_id = ev_res.json()["id"]

    gal_res = await client.post(
        "/api/v1/galleries",
        headers=admin_headers,
        json={"event_id": event_id, "name": "Summit Highlights", "pin": "123456"}
    )
    gallery_id = gal_res.json()["id"]

    # Team member attempts publish -> 403 Forbidden
    response = await client.post(f"/api/v1/galleries/{gallery_id}/publish", headers=team_headers)
    assert response.status_code == 403
