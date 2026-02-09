from datetime import datetime, time

import pytest
from pydantic import ValidationError

from ftrs_data_layer.domain.availability import (
    AvailableTime,
    AvailableTimePublicHolidays,
    AvailableTimeVariation,
    NotAvailable,
    OpeningTime,
)
from ftrs_data_layer.domain.enums import DayOfWeek, OpeningTimeCategory


class TestAvailableTime:
    """Tests for AvailableTime model."""

    def test_create_available_time(self) -> None:
        """Test creating AvailableTime with all required fields."""
        available_time = AvailableTime(
            dayOfWeek=DayOfWeek.MONDAY,
            startTime=time.fromisoformat("09:00:00"),
            endTime=time.fromisoformat("17:00:00"),
        )

        assert available_time.dayOfWeek == DayOfWeek.MONDAY
        assert available_time.startTime == time.fromisoformat("09:00:00")
        assert available_time.endTime == time.fromisoformat("17:00:00")
        assert available_time.allDay is False
        assert available_time.category == OpeningTimeCategory.AVAILABLE_TIME

    def test_available_time_with_all_day(self) -> None:
        """Test creating AvailableTime with allDay=True."""
        available_time = AvailableTime(
            dayOfWeek=DayOfWeek.TUESDAY,
            startTime=time.fromisoformat("00:00:00"),
            endTime=time.fromisoformat("23:59:59"),
            allDay=True,
        )

        assert available_time.allDay is True

    def test_available_time_model_dump_json(self) -> None:
        """Test AvailableTime serialization to JSON."""
        available_time = AvailableTime(
            dayOfWeek=DayOfWeek.FRIDAY,
            startTime=time.fromisoformat("08:30:00"),
            endTime=time.fromisoformat("18:00:00"),
        )

        dumped = available_time.model_dump(mode="json")

        assert dumped["category"] == "availableTime"
        assert dumped["dayOfWeek"] == "fri"
        assert dumped["startTime"] == "08:30:00"
        assert dumped["endTime"] == "18:00:00"
        assert dumped["allDay"] is False

    def test_available_time_round_trip(self) -> None:
        """Test AvailableTime serialization and deserialization."""
        original = AvailableTime(
            dayOfWeek=DayOfWeek.WEDNESDAY,
            startTime=time.fromisoformat("10:00:00"),
            endTime=time.fromisoformat("16:00:00"),
        )

        dumped = original.model_dump(mode="json")
        reloaded = AvailableTime.model_validate(dumped)

        assert reloaded.dayOfWeek == original.dayOfWeek
        assert reloaded.startTime == original.startTime
        assert reloaded.endTime == original.endTime

    def test_available_time_all_days_of_week(self) -> None:
        """Test AvailableTime with all days of the week."""
        days = [
            DayOfWeek.MONDAY,
            DayOfWeek.TUESDAY,
            DayOfWeek.WEDNESDAY,
            DayOfWeek.THURSDAY,
            DayOfWeek.FRIDAY,
            DayOfWeek.SATURDAY,
            DayOfWeek.SUNDAY,
        ]

        for day in days:
            available_time = AvailableTime(
                dayOfWeek=day,
                startTime=time.fromisoformat("09:00:00"),
                endTime=time.fromisoformat("17:00:00"),
            )
            assert available_time.dayOfWeek == day

    def test_available_time_missing_day_of_week_raises_error(self) -> None:
        """Test that missing dayOfWeek raises ValidationError."""
        with pytest.raises(ValidationError):
            AvailableTime(
                startTime=time.fromisoformat("09:00:00"),
                endTime=time.fromisoformat("17:00:00"),
            )  # type: ignore


class TestAvailableTimeVariation:
    """Tests for AvailableTimeVariation model."""

    def test_create_available_time_variation(self) -> None:
        """Test creating AvailableTimeVariation with all fields."""
        variation = AvailableTimeVariation(
            description="Staff training",
            startTime=datetime.fromisoformat("2025-06-10T10:30:00"),
            endTime=datetime.fromisoformat("2025-06-10T12:30:00"),
        )

        assert variation.description == "Staff training"
        assert variation.startTime == datetime.fromisoformat("2025-06-10T10:30:00")
        assert variation.endTime == datetime.fromisoformat("2025-06-10T12:30:00")
        assert variation.category == OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS

    def test_available_time_variation_without_description(self) -> None:
        """Test creating AvailableTimeVariation without description."""
        variation = AvailableTimeVariation(
            startTime=datetime.fromisoformat("2025-06-10T10:30:00"),
            endTime=datetime.fromisoformat("2025-06-10T12:30:00"),
        )

        assert variation.description is None

    def test_available_time_variation_model_dump_json(self) -> None:
        """Test AvailableTimeVariation serialization to JSON."""
        variation = AvailableTimeVariation(
            description="Holiday hours",
            startTime=datetime.fromisoformat("2025-12-25T08:00:00"),
            endTime=datetime.fromisoformat("2025-12-25T14:00:00"),
        )

        dumped = variation.model_dump(mode="json")

        assert dumped["category"] == "availableTimeVariations"
        assert dumped["description"] == "Holiday hours"
        assert "2025-12-25" in dumped["startTime"]
        assert "2025-12-25" in dumped["endTime"]

    def test_available_time_variation_round_trip(self) -> None:
        """Test AvailableTimeVariation serialization and deserialization."""
        original = AvailableTimeVariation(
            description="Extended hours",
            startTime=datetime.fromisoformat("2025-07-01T07:00:00"),
            endTime=datetime.fromisoformat("2025-07-01T20:00:00"),
        )

        dumped = original.model_dump(mode="json")
        reloaded = AvailableTimeVariation.model_validate(dumped)

        assert reloaded.description == original.description
        assert reloaded.category == OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS


class TestAvailableTimePublicHolidays:
    """Tests for AvailableTimePublicHolidays model."""

    def test_create_available_time_public_holidays(self) -> None:
        """Test creating AvailableTimePublicHolidays."""
        public_holiday = AvailableTimePublicHolidays(
            startTime=time.fromisoformat("12:30:00"),
            endTime=time.fromisoformat("16:30:00"),
        )

        assert public_holiday.startTime == time.fromisoformat("12:30:00")
        assert public_holiday.endTime == time.fromisoformat("16:30:00")
        assert (
            public_holiday.category
            == OpeningTimeCategory.AVAILABLE_TIME_PUBLIC_HOLIDAYS
        )

    def test_available_time_public_holidays_model_dump_json(self) -> None:
        """Test AvailableTimePublicHolidays serialization to JSON."""
        public_holiday = AvailableTimePublicHolidays(
            startTime=time.fromisoformat("09:00:00"),
            endTime=time.fromisoformat("13:00:00"),
        )

        dumped = public_holiday.model_dump(mode="json")

        assert dumped["category"] == "availableTimePublicHolidays"
        assert dumped["startTime"] == "09:00:00"
        assert dumped["endTime"] == "13:00:00"

    def test_available_time_public_holidays_round_trip(self) -> None:
        """Test AvailableTimePublicHolidays serialization and deserialization."""
        original = AvailableTimePublicHolidays(
            startTime=time.fromisoformat("10:00:00"),
            endTime=time.fromisoformat("15:00:00"),
        )

        dumped = original.model_dump(mode="json")
        reloaded = AvailableTimePublicHolidays.model_validate(dumped)

        assert reloaded.startTime == original.startTime
        assert reloaded.endTime == original.endTime


class TestNotAvailable:
    """Tests for NotAvailable model."""

    def test_create_not_available(self) -> None:
        """Test creating NotAvailable with all fields."""
        not_available = NotAvailable(
            description="Closed for renovation",
            startTime=datetime.fromisoformat("2025-07-15T00:00:00"),
            endTime=datetime.fromisoformat("2025-07-15T23:59:59"),
        )

        assert not_available.description == "Closed for renovation"
        assert not_available.startTime == datetime.fromisoformat("2025-07-15T00:00:00")
        assert not_available.endTime == datetime.fromisoformat("2025-07-15T23:59:59")
        assert not_available.category == OpeningTimeCategory.NOT_AVAILABLE

    def test_not_available_without_description(self) -> None:
        """Test creating NotAvailable without description."""
        not_available = NotAvailable(
            startTime=datetime.fromisoformat("2025-08-01T00:00:00"),
            endTime=datetime.fromisoformat("2025-08-01T23:59:59"),
        )

        assert not_available.description is None

    def test_not_available_model_dump_json(self) -> None:
        """Test NotAvailable serialization to JSON."""
        not_available = NotAvailable(
            description="Annual closure",
            startTime=datetime.fromisoformat("2025-12-24T00:00:00"),
            endTime=datetime.fromisoformat("2025-12-26T23:59:59"),
        )

        dumped = not_available.model_dump(mode="json")

        assert dumped["category"] == "notAvailable"
        assert dumped["description"] == "Annual closure"

    def test_not_available_round_trip(self) -> None:
        """Test NotAvailable serialization and deserialization."""
        original = NotAvailable(
            description="Emergency closure",
            startTime=datetime.fromisoformat("2025-09-01T00:00:00"),
            endTime=datetime.fromisoformat("2025-09-02T23:59:59"),
        )

        dumped = original.model_dump(mode="json")
        reloaded = NotAvailable.model_validate(dumped)

        assert reloaded.description == original.description
        assert reloaded.category == OpeningTimeCategory.NOT_AVAILABLE


class TestOpeningTimeDiscriminator:
    """Tests for OpeningTime union type with discriminator."""

    def test_available_time_has_correct_category(self) -> None:
        """Test that AvailableTime has the correct category discriminator."""
        available_time = AvailableTime(
            dayOfWeek=DayOfWeek.MONDAY,
            startTime=time.fromisoformat("09:00:00"),
            endTime=time.fromisoformat("17:00:00"),
        )
        assert available_time.category == OpeningTimeCategory.AVAILABLE_TIME

    def test_available_time_variation_has_correct_category(self) -> None:
        """Test that AvailableTimeVariation has the correct category discriminator."""
        variation = AvailableTimeVariation(
            startTime=datetime.fromisoformat("2025-06-10T10:00:00"),
            endTime=datetime.fromisoformat("2025-06-10T12:00:00"),
        )
        assert variation.category == OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS

    def test_available_time_public_holidays_has_correct_category(self) -> None:
        """Test that AvailableTimePublicHolidays has the correct category discriminator."""
        public_holiday = AvailableTimePublicHolidays(
            startTime=time.fromisoformat("09:00:00"),
            endTime=time.fromisoformat("13:00:00"),
        )
        assert (
            public_holiday.category
            == OpeningTimeCategory.AVAILABLE_TIME_PUBLIC_HOLIDAYS
        )

    def test_not_available_has_correct_category(self) -> None:
        """Test that NotAvailable has the correct category discriminator."""
        not_available = NotAvailable(
            startTime=datetime.fromisoformat("2025-07-15T00:00:00"),
            endTime=datetime.fromisoformat("2025-07-15T23:59:59"),
        )
        assert not_available.category == OpeningTimeCategory.NOT_AVAILABLE
