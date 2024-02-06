# %%
from typing import Optional
from sqlmodel import Field, SQLModel


class Level(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str
    code: int


class Entity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    name: str = Field(index=True)
    code: int
    level_id: int = Field(foreign_key="level.id")
    
    def __hash__(self):
        return self.id


class Variation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    entity_id: int = Field(foreign_key="entity.id")
    name: str = Field(index=True)

    def __hash__(self):
        return self.id


class DiscoveredVariation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, unique=True)
    entity_id: int = Field(foreign_key="entity.id")
    name: str = Field(index=True)
    proposer_email: str

    def __hash__(self):
        return id


class AdminHierarchy(SQLModel, table=True):
    entity_id: int = Field(foreign_key="entity.id", primary_key=True)
    child_id: int = Field(foreign_key="entity.id", primary_key=True)

    def __hash__(self):
        return (self.entity_id, self.child_id)
