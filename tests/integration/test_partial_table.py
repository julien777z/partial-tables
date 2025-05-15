import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from tests.integration.database import BusinessDraft, Business


class TestPartialTable:
    """Test the partial table integration."""

    def _create_business(
        self,
        model: type[Business],
        db_session: Session,
        **kwargs,
    ) -> Business:
        """Create a business."""

        business = db_session.add(model(**kwargs))

        db_session.commit()

        return business

    def test_partial_table_nullable(self, db_session: Session):
        """Test that the partial table allows nullable fields."""

        self._create_business(
            BusinessDraft,
            db_session,
            business_name="Business 1",
        )

        business = db_session.query(BusinessDraft).first()

        assert business.business_name == "Business 1"
        assert business.city is None
        assert business.address is None

    def test_partial_table_raises(self, db_session: Session):
        """Test that the partial table does not allow to create a business without required fields."""

        with pytest.raises(IntegrityError):
            self._create_business(
                Business,
                db_session,
                business_name="Business 2",
            )

    def test_partial_table_required_fields(self, db_session: Session):
        """Test that the partial table has the required fields."""

        self._create_business(
            Business,
            db_session,
            business_name="Business 2",
            city="City 2",
            address="Address 2",
        )

        business = db_session.query(Business).first()

        assert business.business_name == "Business 2"
        assert business.city == "City 2"
        assert business.address == "Address 2"
