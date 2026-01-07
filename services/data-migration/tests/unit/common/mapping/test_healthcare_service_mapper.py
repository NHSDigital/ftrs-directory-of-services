from datetime import UTC, date, datetime, time
from decimal import Decimal
from uuid import UUID

from freezegun import freeze_time
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    AvailableTime,
    AvailableTimePublicHolidays,
    AvailableTimeVariation,
    HealthcareService,
    HealthcareServiceTelecom,
    NotAvailable,
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.domain.enums import TimeUnit
from ftrs_data_layer.domain.legacy.data_models import (
    ServiceAgeRangeData,
    ServiceDayOpeningData,
    ServiceDayOpeningTimeData,
    ServiceSpecifiedOpeningDateData,
    ServiceSpecifiedOpeningTimeData,
)

from common.mapping.healthcare_service import HealthcareServiceMapper
from service_migration.dependencies import ServiceMigrationDependencies


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test that the healthcare service mapper correctly maps a legacy service."""
    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )
    organisation_id = UUID("0fd917b6-608a-59a0-ba62-eba57ec06a0e")
    location_id = UUID("6ef3317e-c6dc-5e27-b36d-577c375eb060")

    result = mapper.map(
        mock_legacy_service,
        organisation_id,
        location_id,
        category="GP Services",
        type="GP Consultation Service",
    )

    assert isinstance(result, HealthcareService)
    assert result.id == UUID("903cd48b-5d0f-532f-94f4-937a4517b14d")
    assert result.createdBy == "DATA_MIGRATION"
    assert result.createdDateTime == datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    assert result.modifiedBy == "DATA_MIGRATION"
    assert result.modifiedDateTime == datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    assert result.identifier_oldDoS_uid == "test-uid"
    assert result.active is True
    assert result.category == "GP Services"
    assert result.type == "GP Consultation Service"
    assert result.providedBy == organisation_id
    assert result.location == location_id
    assert result.name == "Test Service"
    assert isinstance(result.telecom, HealthcareServiceTelecom)
    assert result.telecom.phone_public == "01234 567890"
    assert result.telecom.phone_private == "09876 543210"
    assert result.telecom.email == "firstname.lastname@nhs.net"
    assert result.telecom.web == "http://example.com"


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map_opening_times(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test that the healthcare service mapper correctly maps opening times."""
    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )
    organisation_id = UUID("0fd917b6-608a-59a0-ba62-eba57ec06a0e")
    location_id = UUID("6ef3317e-c6dc-5e27-b36d-577c375eb060")

    result = mapper.map(
        mock_legacy_service,
        organisation_id,
        location_id,
        category="GP Services",
        type="GP Consultation Service",
    )

    assert len(result.openingTime) == 10

    # Verify scheduled opening times
    assert result.openingTime[0] == AvailableTime(
        category="availableTime",
        dayOfWeek="mon",
        startTime=time(9, 0),
        endTime=time(17, 0),
        allDay=False,
    )
    assert result.openingTime[1] == AvailableTime(
        category="availableTime",
        dayOfWeek="tue",
        startTime=time(9, 0),
        endTime=time(17, 0),
        allDay=False,
    )
    assert result.openingTime[2] == AvailableTime(
        category="availableTime",
        dayOfWeek="wed",
        startTime=time(9, 0),
        endTime=time(12, 0),
        allDay=False,
    )
    assert result.openingTime[3] == AvailableTime(
        category="availableTime",
        dayOfWeek="wed",
        startTime=time(13, 0),
        endTime=time(17, 0),
        allDay=False,
    )
    assert result.openingTime[4] == AvailableTime(
        category="availableTime",
        dayOfWeek="thu",
        startTime=time(9, 0),
        endTime=time(17, 0),
        allDay=False,
    )
    assert result.openingTime[5] == AvailableTime(
        category="availableTime",
        dayOfWeek="fri",
        startTime=time(9, 0),
        endTime=time(17, 0),
        allDay=False,
    )
    assert result.openingTime[6] == AvailableTime(
        category="availableTime",
        dayOfWeek="sat",
        startTime=time(10, 0),
        endTime=time(14, 0),
        allDay=False,
    )
    assert result.openingTime[7] == AvailableTimePublicHolidays(
        category="availableTimePublicHolidays",
        startTime=time(10, 0),
        endTime=time(14, 0),
    )

    # Verify specified opening times
    assert result.openingTime[8] == AvailableTimeVariation(
        category="availableTimeVariations",
        description=None,
        startTime=datetime(2023, 1, 1, 10, 0),
        endTime=datetime(2023, 1, 1, 14, 0),
    )
    assert result.openingTime[9] == NotAvailable(
        category="notAvailable",
        description=None,
        startTime=datetime(2023, 1, 2, 0, 0),
        endTime=datetime(2023, 1, 2, 23, 59, 59),
    )


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map_scheduled_opening_times(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test mapping of scheduled opening times."""
    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )

    scheduled_times = [
        ServiceDayOpeningData(
            id=1,
            serviceid=1,
            dayid=1,
            times=[
                ServiceDayOpeningTimeData(
                    id=1,
                    starttime=time.fromisoformat("09:00:00"),
                    endtime=time.fromisoformat("17:00:00"),
                    servicedayopeningid=1,
                )
            ],
        ),
        ServiceDayOpeningData(
            id=2,
            serviceid=1,
            dayid=8,
            times=[
                ServiceDayOpeningTimeData(
                    id=2,
                    starttime=time.fromisoformat("10:00:00"),
                    endtime=time.fromisoformat("16:00:00"),
                    servicedayopeningid=2,
                )
            ],
        ),
    ]

    result = mapper.map_scheduled_opening_times(scheduled_times)

    assert len(result) == 2
    assert result[0] == AvailableTime(
        category="availableTime",
        dayOfWeek="mon",
        startTime=time(9, 0),
        endTime=time(17, 0),
        allDay=False,
    )
    assert result[1] == AvailableTimePublicHolidays(
        category="availableTimePublicHolidays",
        startTime=time(10, 0),
        endTime=time(16, 0),
    )


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map_specified_opening_times(
    mock_dependencies: ServiceMigrationDependencies,
) -> None:
    """Test mapping of specified opening times."""
    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )

    specified_times = [
        ServiceSpecifiedOpeningDateData(
            id=1,
            serviceid=1,
            date=date.fromisoformat("2025-07-15"),
            times=[
                ServiceSpecifiedOpeningTimeData(
                    id=1,
                    isclosed=False,
                    starttime=time.fromisoformat("08:00:00"),
                    endtime=time.fromisoformat("12:00:00"),
                    servicespecifiedopeningdateid=1,
                ),
                ServiceSpecifiedOpeningTimeData(
                    id=2,
                    isclosed=False,
                    starttime=time.fromisoformat("13:00:00"),
                    endtime=time.fromisoformat("18:00:00"),
                    servicespecifiedopeningdateid=1,
                ),
            ],
        ),
        ServiceSpecifiedOpeningDateData(
            id=2,
            serviceid=1,
            date=date.fromisoformat("2025-07-16"),
            times=[
                ServiceSpecifiedOpeningTimeData(
                    id=3,
                    isclosed=True,
                    starttime=time.fromisoformat("00:00:00"),
                    endtime=time.fromisoformat("23:59:59"),
                    servicespecifiedopeningdateid=2,
                )
            ],
        ),
    ]

    result = mapper.map_specified_opening_times(specified_times)

    assert len(result) == 3
    assert result[0] == AvailableTimeVariation(
        category="availableTimeVariations",
        description=None,
        startTime=datetime(2025, 7, 15, 8, 0),
        endTime=datetime(2025, 7, 15, 12, 0),
    )
    assert result[1] == AvailableTimeVariation(
        category="availableTimeVariations",
        description=None,
        startTime=datetime(2025, 7, 15, 13, 0),
        endTime=datetime(2025, 7, 15, 18, 0),
    )
    assert result[2] == NotAvailable(
        category="notAvailable",
        description=None,
        startTime=datetime(2025, 7, 16, 0, 0),
        endTime=datetime(2025, 7, 16, 23, 59, 59),
    )


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map_sgsds(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test mapping of symptom group/symptom discriminator pairs."""
    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )

    result = mapper.map_sgsds(mock_legacy_service)

    assert len(result) == 2
    assert result[0] == SymptomGroupSymptomDiscriminatorPair(
        sg=1035,
        sd=4003,
    )
    assert result[1] == SymptomGroupSymptomDiscriminatorPair(
        sg=360,
        sd=14023,
    )


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map_dispositions(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test mapping of dispositions."""
    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )

    result = mapper.map_dispositions(mock_legacy_service)

    assert len(result) == 2
    assert "DX115" in result
    assert "DX12" in result


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map_age_eligibility_criteria_single_range(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test mapping of age eligibility criteria with a single range."""
    mock_legacy_service.age_range = [
        ServiceAgeRangeData(
            id=1,
            serviceid=1,
            daysfrom=Decimal(0),
            daysto=Decimal("364.25"),
        ),
    ]

    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )

    result = mapper.map_age_eligibility_criteria(mock_legacy_service)

    assert result is not None
    assert len(result) == 1
    assert result[0]["rangeFrom"] == Decimal(0)
    assert result[0]["rangeTo"] == Decimal("364.25")
    assert result[0]["type"] == TimeUnit.DAYS


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map_age_eligibility_criteria_consecutive_ranges(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test mapping of age eligibility criteria with consecutive ranges."""
    mock_legacy_service.age_range = [
        ServiceAgeRangeData(
            id=1,
            serviceid=1,
            daysfrom=Decimal(0),
            daysto=Decimal("364.25"),
        ),
        ServiceAgeRangeData(
            id=2,
            serviceid=1,
            daysfrom=Decimal("365.25"),
            daysto=Decimal("1825.25"),
        ),
    ]

    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )

    result = mapper.map_age_eligibility_criteria(mock_legacy_service)

    assert result is not None
    assert len(result) == 1
    assert result[0]["rangeFrom"] == Decimal(0)
    assert result[0]["rangeTo"] == Decimal("1825.25")
    assert result[0]["type"] == TimeUnit.DAYS


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map_age_eligibility_criteria_non_consecutive_ranges(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test mapping of age eligibility criteria with non-consecutive ranges."""
    mock_legacy_service.age_range = [
        ServiceAgeRangeData(
            id=1,
            serviceid=1,
            daysfrom=Decimal(0),
            daysto=Decimal("364.25"),
        ),
        ServiceAgeRangeData(
            id=2,
            serviceid=1,
            daysfrom=Decimal("1826.25"),
            daysto=Decimal(5843),
        ),
    ]

    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )

    result = mapper.map_age_eligibility_criteria(mock_legacy_service)

    assert result is not None
    assert len(result) == 2
    assert result[0]["rangeFrom"] == Decimal(0)
    assert result[0]["rangeTo"] == Decimal("364.25")
    assert result[1]["rangeFrom"] == Decimal("1826.25")
    assert result[1]["rangeTo"] == Decimal(5843)


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map_age_eligibility_criteria_overlapping_ranges(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
) -> None:
    """Test mapping of age eligibility criteria with overlapping ranges."""
    mock_legacy_service.age_range = [
        ServiceAgeRangeData(
            id=1,
            serviceid=1,
            daysfrom=Decimal(0),
            daysto=Decimal(500),
        ),
        ServiceAgeRangeData(
            id=2,
            serviceid=1,
            daysfrom=Decimal(400),
            daysto=Decimal(1000),
        ),
    ]

    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )

    result = mapper.map_age_eligibility_criteria(mock_legacy_service)

    assert result is not None
    assert len(result) == 1
    assert result[0]["rangeFrom"] == Decimal(0)
    assert result[0]["rangeTo"] == Decimal(1000)


@freeze_time("2025-07-25T12:00:00")
def test_healthcare_service_mapper_map_age_eligibility_criteria_no_range(
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: dict,
    mock_logger: MockLogger,
) -> None:
    """Test mapping of age eligibility criteria with no age range."""
    mock_legacy_service.age_range = []

    mapper = HealthcareServiceMapper(
        deps=mock_dependencies, start_time=datetime(2025, 7, 25, 12, 0, 0, tzinfo=UTC)
    )

    result = mapper.map_age_eligibility_criteria(mock_legacy_service)

    assert result is None
    # Should have logged the missing age range
    assert len(mock_logger.logs) > 0
