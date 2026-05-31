import pytest


@pytest.fixture
async def baby(client):
    r = await client.post("/api/v1/babies", json={"name": "Alice", "birth_date": 1705276800})
    return r.json()


async def test_log_breast_feeding(client, baby):
    r = await client.post(
        f"/api/v1/babies/{baby['id']}/feedings",
        json={
            "feeding_type": "breast",
            "side": "left",
            "duration_seconds": 900,
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["feeding_type"] == "breast"
    assert data["side"] == "left"
    assert data["amount_ml"] is None


async def test_log_bottle_feeding(client, baby):
    r = await client.post(
        f"/api/v1/babies/{baby['id']}/feedings",
        json={
            "feeding_type": "bottle",
            "amount_ml": 120,
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["feeding_type"] == "bottle"
    assert data["amount_ml"] == 120
    assert data["side"] is None


async def test_list_feedings(client, baby):
    for _ in range(3):
        await client.post(
            f"/api/v1/babies/{baby['id']}/feedings",
            json={
                "feeding_type": "bottle",
                "amount_ml": 100,
            },
        )
    r = await client.get(f"/api/v1/babies/{baby['id']}/feedings")
    assert r.status_code == 200
    assert len(r.json()) == 3


async def test_delete_feeding(client, baby):
    r = await client.post(
        f"/api/v1/babies/{baby['id']}/feedings",
        json={
            "feeding_type": "bottle",
            "amount_ml": 80,
        },
    )
    fid = r.json()["id"]
    r = await client.delete(f"/api/v1/babies/{baby['id']}/feedings/{fid}")
    assert r.status_code == 204
    r = await client.get(f"/api/v1/babies/{baby['id']}/feedings/{fid}")
    assert r.status_code == 404


async def test_feeding_not_found_for_wrong_baby(client, baby):
    r2 = await client.post("/api/v1/babies", json={"name": "Bob", "birth_date": 1706745600})
    other_baby = r2.json()
    r = await client.post(
        f"/api/v1/babies/{baby['id']}/feedings",
        json={
            "feeding_type": "bottle",
            "amount_ml": 90,
        },
    )
    fid = r.json()["id"]
    r = await client.get(f"/api/v1/babies/{other_baby['id']}/feedings/{fid}")
    assert r.status_code == 404
