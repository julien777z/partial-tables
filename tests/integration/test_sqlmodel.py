import pytest
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from tests.integration.database.sqlmodel_tables import (
    Business,
    BusinessDraft,
    OverrideBusiness,
    OverrideBusinessDraft,
)


class TestSQLModelPartialTableIntegration:
    """Test the SQLModel partial table integration."""

    def _create_business(
        self,
        model: type[Business],
        sqlmodel_session: Session,
        **kwargs,
    ) -> None:
        """Create a business."""

        sqlmodel_session.add(model(**kwargs))
        sqlmodel_session.commit()

    def test_columns_nullable_flags(self):
        """Columns should reflect nullability based on PartialAllowed markers."""

        draft_cols = {c.name: c for c in BusinessDraft.__table__.columns}
        full_cols = {c.name: c for c in Business.__table__.columns}

        assert draft_cols["city"].nullable is True
        assert draft_cols["address"].nullable is True

        assert full_cols["city"].nullable is False
        assert full_cols["address"].nullable is False

    def test_preserves_column_attributes_on_partial(self):
        """Ensure attributes like unique/index are preserved on Partial tables."""

        draft_table = BusinessDraft.__table__
        full_table = Business.__table__

        def _has_unique(table, col_name: str) -> bool:
            col = table.c[col_name]

            if getattr(col, "unique", False):
                return True

            for cons in table.constraints:
                if isinstance(cons, UniqueConstraint):
                    cons_cols = [c.key for c in cons.columns]

                    if cons_cols == [col_name]:
                        return True

            for idx in table.indexes:
                if isinstance(idx, Index) and idx.unique:
                    idx_cols = [c.key for c in idx.columns]

                    if idx_cols == [col_name]:
                        return True

            return False

        def _has_index(table, col_name: str) -> bool:
            col = table.c[col_name]

            if getattr(col, "index", False):
                return True

            for idx in table.indexes:
                if isinstance(idx, Index) and not idx.unique:
                    idx_cols = [c.key for c in idx.columns]

                    if idx_cols == [col_name]:
                        return True
            return False

        # The non-partial table carries the unique/index options from the base.
        assert _has_unique(full_table, "city") is True
        assert _has_index(full_table, "address") is True

        # The partial table must preserve those same options while making the
        # columns nullable, and must not share them destructively with its sibling.
        assert _has_unique(draft_table, "city") is True
        assert _has_index(draft_table, "address") is True
        assert draft_table.c["city"].nullable is True
        assert draft_table.c["address"].nullable is True

    def test_partial_table_field_redeclaration_overrides_base(self):
        """A field redeclared on the partial table keeps its own options, not the base's."""

        draft_city = OverrideBusinessDraft.__table__.c["city"]
        full_city = OverrideBusiness.__table__.c["city"]

        assert full_city.unique is True
        assert full_city.nullable is False

        assert draft_city.index is True
        assert draft_city.unique is not True
        assert draft_city.nullable is True

    def test_partial_table_nullable(self, sqlmodel_session: Session):
        """Test that the SQLModel partial table allows nullable fields."""

        self._create_business(
            BusinessDraft,
            sqlmodel_session,
            business_id=1,
            business_name="Business 1",
            city=None,
            address=None,
        )

        new_business = sqlmodel_session.get(BusinessDraft, 1)

        assert new_business.business_name == "Business 1"
        assert new_business.city is None
        assert new_business.address is None

    def test_partial_table_raises(self, sqlmodel_session: Session):
        """Test that the SQLModel partial table does not allow to create a business without required fields."""

        with pytest.raises(IntegrityError):
            self._create_business(
                Business,
                sqlmodel_session,
                business_id=2,
                business_name="Business 2",
                city=None,
                address=None,
            )

    def test_partial_table_required_fields(self, sqlmodel_session: Session):
        """Test that the SQLModel partial table has the required fields."""

        self._create_business(
            Business,
            sqlmodel_session,
            business_id=2,
            business_name="Business 2",
            city="City 2",
            address="Address 2",
        )

        new_business = sqlmodel_session.get(Business, 2)

        assert new_business.city == "City 2"
        assert new_business.address == "Address 2"
