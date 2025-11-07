import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from tests.integration.database.sqlalchemy_tables import (
    BusinessDraft,
    Business,
)


class TestSQLAlchemyPartialTable:
    """Test the SQLAlchemy partial table integration."""

    def _create_business(
        self,
        model: type[Business],
        sqlalchemy_session: Session,
        **kwargs,
    ) -> None:
        """Create a business."""

        sqlalchemy_session.add(model(**kwargs))
        sqlalchemy_session.commit()

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

        draft_cols = {c.name: c for c in BusinessDraft.__table__.columns}
        full_cols = {c.name: c for c in Business.__table__.columns}

        assert draft_cols["city"].unique is True
        assert draft_cols["address"].index is True

        # Also ensure the non-partial table still has the same attributes
        assert full_cols["city"].unique is True
        assert full_cols["address"].index is True

    def test_partial_table_nullable(self, sqlalchemy_session: Session):
        """Test that the SQLAlchemy partial table allows nullable fields."""

        self._create_business(
            BusinessDraft,
            sqlalchemy_session,
            business_id=1,
            business_name="Business 1",
        )

        business = sqlalchemy_session.get(BusinessDraft, 1)

        assert business.business_name == "Business 1"
        assert business.city is None
        assert business.address is None

    def test_partial_table_raises(self, sqlalchemy_session: Session):
        """Test that the SQLAlchemy partial table does not allow to create a business without required fields."""

        with pytest.raises(IntegrityError):
            self._create_business(
                Business,
                sqlalchemy_session,
                business_id=2,
                business_name="Business 2",
            )

    def test_partial_table_required_fields(self, sqlalchemy_session: Session):
        """Test that the SQLAlchemy partial table has the required fields."""

        self._create_business(
            Business,
            sqlalchemy_session,
            business_id=3,
            business_name="Business 3",
            city="City 3",
            address="Address 3",
        )

        business = sqlalchemy_session.get(Business, 3)

        assert business.business_name == "Business 3"
        assert business.city == "City 3"
        assert business.address == "Address 3"
