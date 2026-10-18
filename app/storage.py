"""In-memory listing store. A real service would use a database; this is a
small sample app for agent-implementation exercises, so simplicity wins."""
from __future__ import annotations

from itertools import count

from app.models import Listing, ListingCreate, ListingStatus

_listings: dict[int, Listing] = {}
_id_counter = count(1)


def reset() -> None:
    """Test helper: clear all state between tests."""
    _listings.clear()


def create_listing(data: ListingCreate) -> Listing:
    listing_id = next(_id_counter)
    listing = Listing(id=listing_id, **data.model_dump())
    _listings[listing_id] = listing
    return listing


def get_listing(listing_id: int) -> Listing | None:
    return _listings.get(listing_id)


def mark_sold(listing_id: int) -> Listing | None:
    """Mark a listing sold. Idempotent: marking an already-sold listing again
    is not an error, it just leaves it sold."""
    listing = _listings.get(listing_id)
    if listing is None:
        return None
    updated = listing.model_copy(update={"status": ListingStatus.sold})
    _listings[listing_id] = updated
    return updated


def search_listings(
    category: str | None = None,
    status: ListingStatus | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Listing], int]:
    """Returns (page of results, total matching count). Page numbers < 1 are
    treated as page 1; a page beyond the available results returns an empty list.
    If min_price > max_price, nothing can match, so the result is empty.
    status=None (no filter) returns listings of every status, including sold -
    only an explicit status filter excludes sold listings."""
    results = list(_listings.values())
    if category is not None:
        results = [listing for listing in results if listing.category == category]
    if status is not None:
        results = [listing for listing in results if listing.status == status]
    if min_price is not None:
        results = [listing for listing in results if listing.price >= min_price]
    if max_price is not None:
        results = [listing for listing in results if listing.price <= max_price]

    total = len(results)
    safe_page = max(page, 1)
    start = (safe_page - 1) * page_size
    return results[start : start + page_size], total
