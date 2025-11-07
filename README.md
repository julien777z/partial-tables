# SQLAlchemy Partial Tables

Partial Tables for SQLAlchemy and SQLModel

## Installation

```bash
pip install partial-tables
```

## Scenario

Let's say you have 2 tables, `business_draft` and `business`.

`business_draft` and `business` have the same fields, but `business_draft` should allow most fields to be nullable.

Any business can freely update its draft, but only approved modifications get copied over to `business`.

How can we implement this and reduce redundancy?

## Usage

Any field marked with `PartialAllowed` will be nullable in the partial table, and required in the complete table.

A partial table is any table that sub-classes with `PartialTable`.

## Example (SQLAlchemy Declarative)

```python
from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from partial_tables import PartialSQLAlchemyMixin, PartialAllowed, PartialTable


class Base(DeclarativeBase):
    __abstract__ = True


class BusinessBase(PartialSQLAlchemyMixin, Base):
    """Base class for all business models."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    business_name: Mapped[str] = mapped_column()
    # Mark fields that may be nullable in the partial table
    city: Mapped[Annotated[str, PartialAllowed()]] = mapped_column()
    address: Mapped[Annotated[str, PartialAllowed()]] = mapped_column()


class BusinessDraft(BusinessBase, PartialTable):
    __tablename__ = "business_draft"


class Business(BusinessBase):
    __tablename__ = "business"
```

`Business` has all required (NOT NULL) columns, and `BusinessDraft` has every field marked with `PartialAllowed` as nullable.

## Example (SQLModel)

```python
from typing import Annotated
from sqlmodel import SQLModel, Field
from partial_tables import PartialSQLModelMixin, PartialAllowed, PartialTable


class BusinessBase(PartialSQLModelMixin, SQLModel):
    id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})
    business_name: str
    city: Annotated[str, PartialAllowed()] = Field()
    address: Annotated[str, PartialAllowed()] = Field()


class BusinessDraft(BusinessBase, PartialTable, table=True):
    __tablename__ = "business_draft"


class Business(BusinessBase, table=True):
    __tablename__ = "business"
```

## License
MIT
