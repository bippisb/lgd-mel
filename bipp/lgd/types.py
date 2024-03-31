from pydantic import BaseModel
from enum import Enum


class AdminLevel(Enum):
    india = "india"
    state = "state"
    district = "district"
    sub_district = "sub_district"
    block = "block"
    panchayat = "panchayat"


class MatchItem(BaseModel):
    name: str
    level: AdminLevel | None = None
    parent_id: int | None = None


class GetLGDMatchPayload(BaseModel):
    with_parents: bool = False
    with_community_variations: bool = False
    items: list[MatchItem]


class AddVariationPayload(BaseModel):
    variation: str
    entity_id: str
    email: str