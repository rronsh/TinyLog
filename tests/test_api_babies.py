import pytest


@pytest.fixture
async def baby(client):
    r = await client.post(
        "/api/v1/babies",
        json={
            "name": "Alice",
            "birth_date": 1705276800,
            "avatar_color": "#FF9AA2",
        },
    )
    assert r.status_code == 201
    return r.json()


async def test_create_baby(client):
    r = await client.post(
        "/api/v1/babies",
        json={
            "name": "Bob",
            "birth_date": 1717200000,
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Bob"
    assert "id" in data


async def test_list_babies(client, baby):
    r = await client.get("/api/v1/babies")
    assert r.status_code == 200
    assert any(b["id"] == baby["id"] for b in r.json())


async def test_get_baby(client, baby):
    r = await client.get(f"/api/v1/babies/{baby['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Alice"


async def test_get_baby_not_found(client):
    from uuid import uuid7

    r = await client.get(f"/api/v1/babies/{uuid7()}")
    assert r.status_code == 404


async def test_update_baby(client, baby):
    r = await client.patch(f"/api/v1/babies/{baby['id']}", json={"name": "Alicia"})
    assert r.status_code == 200
    assert r.json()["name"] == "Alicia"


async def test_delete_baby(client, baby):
    r = await client.delete(f"/api/v1/babies/{baby['id']}")
    assert r.status_code == 204
    r = await client.get(f"/api/v1/babies/{baby['id']}")
    assert r.status_code == 404
