import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_public_customer_gallery_flow(
    client: AsyncClient,
    admin_headers,
    team_headers,
    team_user
):
    # 1. Admin creates event
    ev_res = await client.post(
        "/api/v1/events",
        headers=admin_headers,
        json={"name": "Product Launch Gala", "event_date": "2026-10-10"}
    )
    event_id = ev_res.json()["id"]

    # 2. Admin assigns team member
    await client.post(
        f"/api/v1/events/{event_id}/members",
        headers=admin_headers,
        json={"user_id": team_user.id}
    )

    # 3. Team member uploads a photo
    dummy_jpg = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444'9=82<.342\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xFF\xDA\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xFF\xD9"
    files = [("files", ("test_keynote.jpg", dummy_jpg, "image/jpeg"))]
    up_res = await client.post(
        f"/api/v1/events/{event_id}/photos",
        headers=team_headers,
        files=files
    )
    assert up_res.status_code == 201
    photo_id = up_res.json()[0]["id"]

    # 4. Admin creates gallery
    gal_res = await client.post(
        "/api/v1/galleries",
        headers=admin_headers,
        json={
            "event_id": event_id,
            "name": "Launch Highlights",
            "pin": "987654",
            "photo_ids": [photo_id]
        }
    )
    assert gal_res.status_code == 201
    gallery_data = gal_res.json()
    gallery_id = gallery_data["id"]
    slug = gallery_data["slug"]

    # 5. Customer attempts to view draft gallery metadata -> 404
    meta_fail = await client.get(f"/api/v1/public/galleries/{slug}")
    assert meta_fail.status_code == 404

    # 6. Admin publishes gallery
    pub_res = await client.post(
        f"/api/v1/galleries/{gallery_id}/publish",
        headers=admin_headers
    )
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "PUBLISHED"

    # 7. Customer views published gallery metadata -> 200
    meta_ok = await client.get(f"/api/v1/public/galleries/{slug}")
    assert meta_ok.status_code == 200
    assert meta_ok.json()["name"] == "Launch Highlights"

    # 8. Customer enters WRONG PIN -> 401
    wrong_pin = await client.post(
        f"/api/v1/public/galleries/{slug}/verify",
        json={"pin": "000000"}
    )
    assert wrong_pin.status_code == 401
    assert "Incorrect gallery PIN" in wrong_pin.json()["detail"]

    # 9. Customer enters CORRECT PIN -> 200 & receive token
    correct_pin = await client.post(
        f"/api/v1/public/galleries/{slug}/verify",
        json={"pin": "987654"}
    )
    assert correct_pin.status_code == 200
    gallery_token = correct_pin.json()["gallery_access_token"]
    assert gallery_token is not None

    # 10. Customer fetches published photos using token -> 200
    photos_res = await client.get(
        f"/api/v1/public/galleries/{slug}/photos",
        headers={"X-Gallery-Token": gallery_token}
    )
    assert photos_res.status_code == 200
    photos_data = photos_res.json()
    assert len(photos_data) == 1
    assert photos_data[0]["id"] == photo_id

@pytest.mark.asyncio
async def test_gallery_token_cross_access_rejection(client: AsyncClient, admin_headers):
    # Create Gallery A
    ev_a = await client.post("/api/v1/events", headers=admin_headers, json={"name": "Event A", "event_date": "2026-01-01"})
    gal_a = await client.post("/api/v1/galleries", headers=admin_headers, json={"event_id": ev_a.json()["id"], "name": "Gal A", "pin": "111111"})
    await client.post(f"/api/v1/galleries/{gal_a.json()['id']}/publish", headers=admin_headers)
    tok_a_res = await client.post(f"/api/v1/public/galleries/{gal_a.json()['slug']}/verify", json={"pin": "111111"})
    token_a = tok_a_res.json()["gallery_access_token"]

    # Create Gallery B
    ev_b = await client.post("/api/v1/events", headers=admin_headers, json={"name": "Event B", "event_date": "2026-01-02"})
    gal_b = await client.post("/api/v1/galleries", headers=admin_headers, json={"event_id": ev_b.json()["id"], "name": "Gal B", "pin": "222222"})
    await client.post(f"/api/v1/galleries/{gal_b.json()['id']}/publish", headers=admin_headers)

    # Use Token A against Gallery B -> Expect 403 Forbidden!
    response = await client.get(
        f"/api/v1/public/galleries/{gal_b.json()['slug']}/photos",
        headers={"X-Gallery-Token": token_a}
    )
    assert response.status_code == 403
    assert "different gallery" in response.json()["detail"]
