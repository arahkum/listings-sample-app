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


@app.get("/listings", response_model=ListingSearchResult)
def search_listings(
    category: str | None = None,
    page: int = Query(default=1, ge=1),
) -> ListingSearchResult:
    items, total = storage.search_listings(category=category, status=ListingStatus.active, page=page)
    return ListingSearchResult(items=items, total=total, page=page)
