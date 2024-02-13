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


class AddVariationPayload(BaseModel):
    variation: str
    entity_id: str