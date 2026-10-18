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


def search_listings(
    category: str | None = None,
    status: ListingStatus | None = ListingStatus.active,
) -> list[Listing]:
    results = list(_listings.values())
    if category is not None:
        results = [listing for listing in results if listing.category == category]
    if status is not None:
        results = [listing for listing in results if listing.status == status]
    return results
