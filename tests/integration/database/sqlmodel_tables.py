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

    business_id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})
    business_name: str
    city: Annotated[str, PartialAllowed()] = Field(unique=True)
    address: Annotated[str, PartialAllowed()] = Field(index=True)


class BusinessDraft(SQLModelBusinessBase, PartialTable, table=True):
    __tablename__ = "business_draft"


class Business(SQLModelBusinessBase, table=True):
    __tablename__ = "business"
