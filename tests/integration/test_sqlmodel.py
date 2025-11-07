import pytest
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from tests.integration.database.sqlmodel_tables import BusinessDraft, Business


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

    def test_columns_nullable_flags(self, sqlmodel_session: Session):
        """Columns should reflect nullability based on PartialAllowed markers."""

        draft_cols = {c.name: c for c in BusinessDraft.__table__.columns}
        full_cols = {c.name: c for c in Business.__table__.columns}

        assert draft_cols["city"].nullable is True
        assert draft_cols["address"].nullable is True

        assert full_cols["city"].nullable is False
        assert full_cols["address"].nullable is False

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
