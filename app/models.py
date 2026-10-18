from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ListingStatus(str, Enum):
    active = "active"
    sold = "sold"


class ListingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    price: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)


class Listing(ListingCreate):
    id: int
    status: ListingStatus = ListingStatus.active


class ListingSearchResult(BaseModel):
    items: list[Listing]
    total: int
    page: int
