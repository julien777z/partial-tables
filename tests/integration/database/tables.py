from typing import Annotated
from abc import ABC
from sqlmodel import Field, SQLModel
from partial_table import PartialBase, PartialAllowed, PartialTable

__all__ = [
    "Base",
    "BusinessBase",
    "BusinessDraft",
    "Business",
]


class Base(ABC, SQLModel):
    """Base class for all models."""

    id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})


class BusinessBase(PartialBase, Base):
    """Base class for all business models."""

    business_name: str
    city: Annotated[str, PartialAllowed()] = Field()
    address: Annotated[str, PartialAllowed()] = Field()


class BusinessDraft(BusinessBase, PartialTable, table=True):
    __tablename__ = "business_draft"


class Business(BusinessBase, table=True):
    __tablename__ = "business"
