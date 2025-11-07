from typing import Annotated
from sqlmodel import SQLModel, Field
from partial_tables import PartialSQLModelMixin, PartialAllowed, PartialTable

__all__ = [
    "SQLModelBusinessBase",
    "BusinessDraft",
    "Business",
]


class SQLModelBusinessBase(PartialSQLModelMixin, SQLModel):
    """Base model shared by both tables."""

    id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})
    business_name: str
    city: Annotated[str, PartialAllowed()] = Field()
    address: Annotated[str, PartialAllowed()] = Field()


class BusinessDraft(SQLModelBusinessBase, PartialTable, table=True):
    __tablename__ = "business_draft"


class Business(SQLModelBusinessBase, table=True):
    __tablename__ = "business"
