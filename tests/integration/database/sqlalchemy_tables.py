from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from partial_tables import PartialSQLAlchemyMixin, PartialAllowed, PartialTable

__all__ = [
    "SQLAlchemyBusinessBase",
    "BusinessBase",
    "BusinessDraft",
    "Business",
]


class SQLAlchemyBusinessBase(DeclarativeBase):
    """Base class for all business models."""

    __abstract__ = True


class BusinessBase(PartialSQLAlchemyMixin, SQLAlchemyBusinessBase):
    """Base class for all business models."""

    __abstract__ = True

    business_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    business_name: Mapped[str] = mapped_column()
    city: Mapped[Annotated[str, PartialAllowed()]] = mapped_column()
    address: Mapped[Annotated[str, PartialAllowed()]] = mapped_column()


class BusinessDraft(BusinessBase, PartialTable):
    __tablename__ = "business_draft"


class Business(BusinessBase):
    __tablename__ = "business"
