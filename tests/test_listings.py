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


def test_search_filters_by_price_range():
    _create(title="Cheap", price=50.0)
    _create(title="Mid", price=150.0)
    _create(title="Expensive", price=500.0)
    resp = client.get("/listings", params={"min_price": 100, "max_price": 200})
    titles = [listing["title"] for listing in resp.json()["items"]]
    assert titles == ["Mid"]


def test_search_price_range_is_inclusive():
    _create(title="Exactly min", price=100.0)
    _create(title="Exactly max", price=200.0)
    resp = client.get("/listings", params={"min_price": 100, "max_price": 200})
    titles = {listing["title"] for listing in resp.json()["items"]}
    assert titles == {"Exactly min", "Exactly max"}


def test_search_with_only_max_price():
    _create(title="Cheap", price=50.0)
    _create(title="Expensive", price=500.0)
    resp = client.get("/listings", params={"max_price": 100})
    titles = [listing["title"] for listing in resp.json()["items"]]
    assert titles == ["Cheap"]


def test_search_min_price_greater_than_max_price_returns_empty():
    _create(title="Anything", price=100.0)
    resp = client.get("/listings", params={"min_price": 200, "max_price": 100})
    assert resp.json()["items"] == []


def test_search_ignores_non_numeric_price_instead_of_erroring():
    _create(title="Anything", price=100.0)
    resp = client.get("/listings", params={"min_price": "not-a-number"})
    assert resp.status_code == 200
    titles = [listing["title"] for listing in resp.json()["items"]]
    assert "Anything" in titles


def test_mark_listing_sold():
    listing_id = _create(title="Bike").json()["id"]
    resp = client.patch(f"/listings/{listing_id}/sold")
    assert resp.status_code == 200
    assert resp.json()["status"] == "sold"


def test_mark_sold_404_when_missing():
    resp = client.patch("/listings/999/sold")
    assert resp.status_code == 404


def test_marking_already_sold_listing_sold_again_is_not_an_error():
    listing_id = _create(title="Bike").json()["id"]
    client.patch(f"/listings/{listing_id}/sold")
    resp = client.patch(f"/listings/{listing_id}/sold")
    assert resp.status_code == 200
    assert resp.json()["status"] == "sold"


def test_sold_listings_excluded_when_status_filter_applied():
    listing_id = _create(title="Bike").json()["id"]
    client.patch(f"/listings/{listing_id}/sold")
    resp = client.get("/listings", params={"status": "active"})
    titles = [listing["title"] for listing in resp.json()["items"]]
    assert "Bike" not in titles


def test_sold_listings_appear_when_no_status_filter_used():
    listing_id = _create(title="Bike").json()["id"]
    client.patch(f"/listings/{listing_id}/sold")
    resp = client.get("/listings")
    titles = [listing["title"] for listing in resp.json()["items"]]
    assert "Bike" in titles


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
