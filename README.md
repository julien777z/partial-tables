# SQLAlchemy Partial Tables

Partial Tables for SQLAlchemy

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

## Example

```python
from typing import Annotated
from sqlmodel import Field, SQLModel
from partial_tables import PartialBase, PartialAllowed, PartialTable


class BusinessBase(PartialBase, SQLModel):
    """Base class for all business models."""

    id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})

    business_name: str
    city: Annotated[str, PartialAllowed()] = Field()
    address: Annotated[str, PartialAllowed()] = Field()


class BusinessDraft(BusinessBase, PartialTable, table=True):
    __tablename__ = "business_draft"


class Business(BusinessBase, table=True):
    __tablename__ = "business"

```

`Business` has all required fields, and `BusinessDraft` has every field marked with `PartialAllowed` as nullable.

## License
MIT
