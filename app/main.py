from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from app.models import Listing, ListingCreate, ListingSearchResult, ListingStatus
from app import storage

app = FastAPI(title="listings-sample-app")


@app.post("/listings", response_model=Listing, status_code=201)
def create_listing(data: ListingCreate) -> Listing:
    return storage.create_listing(data)


@app.get("/listings/{listing_id}", response_model=Listing)
def get_listing(listing_id: int) -> Listing:
    listing = storage.get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@app.patch("/listings/{listing_id}/sold", response_model=Listing)
def mark_listing_sold(listing_id: int) -> Listing:
    listing = storage.mark_sold(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


def _parse_price(value: str | None) -> float | None:
    """Per spec: a non-numeric price value is ignored (treated as not
    provided), not rejected with an error."""
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


@app.get("/listings", response_model=ListingSearchResult)
def search_listings(
    category: str | None = None,
    status: ListingStatus | None = None,
    min_price: str | None = None,
    max_price: str | None = None,
    page: int = Query(default=1, ge=1),
) -> ListingSearchResult:
    items, total = storage.search_listings(
        category=category,
        status=status,
        min_price=_parse_price(min_price),
        max_price=_parse_price(max_price),
        page=page,
    )
    return ListingSearchResult(items=items, total=total, page=page)
