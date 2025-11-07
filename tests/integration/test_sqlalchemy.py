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
    ) -> Business:
        """Create a business."""

        business = sqlalchemy_session.add(model(**kwargs))

        sqlalchemy_session.commit()

        return business

    def test_partial_table_nullable(self, sqlalchemy_session: Session):
        """Test that the SQLAlchemy partial table allows nullable fields."""

        self._create_business(
            BusinessDraft,
            sqlalchemy_session,
            business_name="Business 1",
        )

        business = sqlalchemy_session.query(BusinessDraft).first()

        assert business.business_name == "Business 1"
        assert business.city is None
        assert business.address is None

    def test_partial_table_raises(self, sqlalchemy_session: Session):
        """Test that the SQLAlchemy partial table does not allow to create a business without required fields."""

        with pytest.raises(IntegrityError):
            self._create_business(
                Business,
                sqlalchemy_session,
                business_name="Business 2",
            )

    def test_partial_table_required_fields(self, sqlalchemy_session: Session):
        """Test that the SQLAlchemy partial table has the required fields."""

        self._create_business(
            Business,
            sqlalchemy_session,
            business_name="Business 2",
            city="City 2",
            address="Address 2",
        )

        business = sqlalchemy_session.query(Business).first()

        assert business.business_name == "Business 2"
        assert business.city == "City 2"
        assert business.address == "Address 2"
