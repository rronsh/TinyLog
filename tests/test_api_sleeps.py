import pytest


@pytest.fixture
async def baby(client):
    r = await client.post("/api/v1/babies", json={"name": "Alice", "birth_date": 1705276800})
    return r.json()


async def test_start_sleep(client, baby):
    r = await client.post(f"/api/v1/babies/{baby['id']}/sleeps", json={})
    assert r.status_code == 201
    data = r.json()
    assert data["end_time"] is None
    assert data["duration_seconds"] is None


async def test_end_sleep(client, baby):
    r = await client.post(f"/api/v1/babies/{baby['id']}/sleeps", json={})
    sid = r.json()["id"]

    r = await client.post(f"/api/v1/babies/{baby['id']}/sleeps/{sid}/end", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["end_time"] is not None
    assert data["duration_seconds"] is not None
    assert data["duration_seconds"] >= 0


async def test_end_sleep_twice_fails(client, baby):
    r = await client.post(f"/api/v1/babies/{baby['id']}/sleeps", json={})
    sid = r.json()["id"]
    await client.post(f"/api/v1/babies/{baby['id']}/sleeps/{sid}/end", json={})
    r = await client.post(f"/api/v1/babies/{baby['id']}/sleeps/{sid}/end", json={})
    assert r.status_code == 400


async def test_list_active_sleeps(client, baby):
    await client.post(f"/api/v1/babies/{baby['id']}/sleeps", json={})
    r = await client.get(f"/api/v1/babies/{baby['id']}/sleeps?active=true")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["end_time"] is None


async def test_list_completed_sleeps(client, baby):
    r = await client.post(f"/api/v1/babies/{baby['id']}/sleeps", json={})
    sid = r.json()["id"]
    await client.post(f"/api/v1/babies/{baby['id']}/sleeps/{sid}/end", json={})

    r = await client.get(f"/api/v1/babies/{baby['id']}/sleeps?active=false")
    assert r.status_code == 200
    assert all(s["end_time"] is not None for s in r.json())


async def test_delete_sleep(client, baby):
    r = await client.post(f"/api/v1/babies/{baby['id']}/sleeps", json={})
    sid = r.json()["id"]
    r = await client.delete(f"/api/v1/babies/{baby['id']}/sleeps/{sid}")
    assert r.status_code == 204
    r = await client.get(f"/api/v1/babies/{baby['id']}/sleeps/{sid}")
    assert r.status_code == 404
