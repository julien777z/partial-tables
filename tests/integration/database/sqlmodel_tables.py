from typing import Annotated

from sqlmodel import Field, SQLModel

from partial_tables import PartialAllowed, PartialSQLModelMixin, PartialTable

__all__ = [
    "SQLModelBusinessBase",
    "BusinessDraft",
    "Business",
    "OverrideBusinessBase",
    "OverrideBusinessDraft",
    "OverrideBusiness",
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


class OverrideBusinessBase(PartialSQLModelMixin, SQLModel):
    """Base model whose partial table redeclares one of its fields."""

    business_id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})
    city: Annotated[str, PartialAllowed()] = Field(unique=True)


class OverrideBusinessDraft(OverrideBusinessBase, PartialTable, table=True):
    __tablename__ = "override_business_draft"

    city: Annotated[str, PartialAllowed()] = Field(index=True)


class OverrideBusiness(OverrideBusinessBase, table=True):
    __tablename__ = "override_business"
