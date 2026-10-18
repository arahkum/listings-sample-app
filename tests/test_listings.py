from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import storage


@pytest.fixture(autouse=True)
def _reset_storage():
    storage.reset()
    yield
    storage.reset()


client = TestClient(app)


def _create(title="Bike", price=100.0, category="vehicles"):
    return client.post(
        "/listings",
        json={"title": title, "description": "A nice item", "price": price, "category": category},
    )


def test_create_listing():
    resp = _create()
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Bike"
    assert body["status"] == "active"


def test_create_listing_rejects_invalid_price():
    resp = client.post(
        "/listings",
        json={"title": "Bike", "description": "x", "price": -5, "category": "vehicles"},
    )
    assert resp.status_code == 422


def test_search_returns_created_listing():
    _create(title="Bike")
    resp = client.get("/listings")
    assert resp.status_code == 200
    body = resp.json()
    titles = [listing["title"] for listing in body["items"]]
    assert "Bike" in titles


def test_search_filters_by_category():
    _create(title="Bike", category="vehicles")
    _create(title="Sofa", category="furniture")
    resp = client.get("/listings", params={"category": "furniture"})
    titles = [listing["title"] for listing in resp.json()["items"]]
    assert titles == ["Sofa"]


def test_get_listing_404_when_missing():
    resp = client.get("/listings/999")
    assert resp.status_code == 404


def test_search_returns_20_per_page_by_default():
    for i in range(25):
        _create(title=f"Item {i}")
    resp = client.get("/listings")
    body = resp.json()
    assert len(body["items"]) == 20
    assert body["total"] == 25
    assert body["page"] == 1


def test_search_page_2_returns_remaining_items():
    for i in range(25):
        _create(title=f"Item {i}")
    resp = client.get("/listings", params={"page": 2})
    body = resp.json()
    assert len(body["items"]) == 5
    assert body["page"] == 2


def test_search_page_beyond_results_returns_empty():
    _create(title="Only item")
    resp = client.get("/listings", params={"page": 999})
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 1


def test_search_page_less_than_1_is_rejected():
    resp = client.get("/listings", params={"page": 0})
    assert resp.status_code == 422
