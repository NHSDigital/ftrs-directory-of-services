from datetime import UTC, date, datetime, time

import pytest
from freezegun import freeze_time
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    Address,
    AvailableTime,
    AvailableTimePublicHolidays,
    AvailableTimeVariation,
    Disposition,
    Endpoint,
    HealthcareService,
    Location,
    NotAvailable,
    Organisation,
    PositionGCS,
    SymptomDiscriminator,
    SymptomGroup,
    SymptomGroupSymptomDiscriminatorPair,
    Telecom,
)
from ftrs_data_layer.domain.legacy import (
    OpeningTimeDay,
    Service,
    ServiceDayOpening,
    ServiceDayOpeningTime,
    ServiceEndpoint,
    ServiceSpecifiedOpeningDate,
    ServiceSpecifiedOpeningTime,
)

from pipeline.transformer import ServiceTransformer
from pipeline.utils.cache import DoSMetadataCache


class BasicServiceTransformer(ServiceTransformer):
    def transform(self, service: Service) -> dict:
        return super().transform(service, validation_issues=[])

    @classmethod
    def is_service_supported(cls, service: Service) -> tuple[bool, str | None]:
        return super().is_service_supported(service)

    @classmethod
    def should_include_service(cls, service: Service) -> tuple[bool, str | None]:
        return super().should_include_service(service)


@freeze_time("2025-07-17T12:00:00")
def test_service_transformer_init(
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger,
        metadata=mock_metadata_cache,
    )

    assert transformer.logger == mock_logger
    assert transformer.metadata == mock_metadata_cache
    assert transformer.start_time == datetime(2025, 7, 17, 12, 0, 0, tzinfo=UTC)

    with pytest.raises(NotImplementedError):
        transformer.transform(None)

    assert transformer.is_service_supported(None) == (False, None)
    assert transformer.should_include_service(None) == (False, None)


def test_service_transformer_abstract_methods(mock_logger: MockLogger) -> None:
    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class ServiceTransformer without an implementation for abstract methods 'is_service_supported', 'should_include_service', 'transform'",
    ):
        ServiceTransformer(logger=mock_logger)


@freeze_time("2025-07-17T12:00:00")
def test_service_transformer_build_organisation(
    mock_logger: MockLogger,
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger, metadata=mock_metadata_cache
    )
    result = transformer.build_organisation(mock_legacy_service)

    assert isinstance(result, Organisation)
    assert result == Organisation(
        id="4539600c-e04e-5b35-a582-9fb36858d0e0",
        name="Test Service",
        type="GP Practice",
        active=True,
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-17T12:00:00Z",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-17T12:00:00Z",
        identifier_ODS_ODSCode="A12345",
        endpoints=[
            Endpoint(
                id="a226aaa5-392c-59c8-8d79-563bb921cb0d",
                createdBy="DATA_MIGRATION",
                createdDateTime="2025-07-17T12:00:00Z",
                modifiedBy="DATA_MIGRATION",
                modifiedDateTime="2025-07-17T12:00:00Z",
                identifier_oldDoS_id=1,
                status="active",
                connectionType="http",
                name=None,
                payloadMimeType=None,
                description="Primary",
                payloadType="urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
                address="http://example.com/endpoint",
                managedByOrganisation="4539600c-e04e-5b35-a582-9fb36858d0e0",
                service=None,
                order=1,
                isCompressionEnabled=True,
            ),
            Endpoint(
                id="4d678d9c-61db-584f-a64c-bd8eb829d8db",
                createdBy="DATA_MIGRATION",
                createdDateTime="2025-07-17T12:00:00Z",
                modifiedBy="DATA_MIGRATION",
                modifiedDateTime="2025-07-17T12:00:00Z",
                identifier_oldDoS_id=2,
                status="active",
                connectionType="email",
                name=None,
                payloadMimeType=None,
                description="Copy",
                payloadType="urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
                address="mailto:test@example.com",
                managedByOrganisation="4539600c-e04e-5b35-a582-9fb36858d0e0",
                service=None,
                order=2,
                isCompressionEnabled=False,
            ),
        ],
    )


@freeze_time("2025-07-17T12:00:00")
def test_build_endpoint(
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger, metadata=mock_metadata_cache
    )

    mock_endpoint = ServiceEndpoint(
        id=12345,
        endpointorder=1,
        transport="itk",
        format="xml",
        interaction="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        businessscenario="Primary",
        address="http://example.com/endpoint1",
        comment="Test Endpoint 1",
        iscompressionenabled="uncompressed",
        serviceid=123456,
    )

    result = transformer.build_endpoint(
        mock_endpoint,
        "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        "01d78de8-4e63-53b3-9b7d-107c39c23a8d",
    )

    assert isinstance(result, Endpoint)
    assert result == Endpoint(
        id="01d78de8-4e63-53b3-9b7d-107c39c23a8d",
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-17T12:00:00Z",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-17T12:00:00Z",
        identifier_oldDoS_id=12345,
        status="active",
        connectionType="itk",
        name=None,
        payloadMimeType="xml",
        description="Primary",
        payloadType="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        address="http://example.com/endpoint1",
        managedByOrganisation="0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        service="01d78de8-4e63-53b3-9b7d-107c39c23a8d",
        order=1,
        isCompressionEnabled=False,
    )


@freeze_time("2025-07-17T12:00:00")
def test_build_endpoint_telno(
    mock_logger: MockLogger, mock_metadata_cache: DoSMetadataCache
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger, metadata=mock_metadata_cache
    )

    mock_endpoint = ServiceEndpoint(
        id=67890,
        endpointorder=2,
        transport="telno",
        format=None,
        interaction="urn:nhs-itk:interaction:primaryEmergencyDepartmentRecipientNHS111CDADocument-v2-0",
        businessscenario="Copy",
        address="tel:01234567890",
        comment="Test Endpoint 2",
        iscompressionenabled=None,
        serviceid=123456,
    )

    result = transformer.build_endpoint(
        mock_endpoint,
        "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        "4f1a685e-15da-5324-b596-6090fc90dc49",
    )

    assert isinstance(result, Endpoint)
    assert result == Endpoint(
        id="4f1a685e-15da-5324-b596-6090fc90dc49",
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-17T12:00:00Z",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-17T12:00:00Z",
        identifier_oldDoS_id=67890,
        status="active",
        connectionType="telno",
        name=None,
        payloadMimeType=None,
        description="Copy",
        payloadType=None,
        address="tel:01234567890",
        managedByOrganisation="0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        service="4f1a685e-15da-5324-b596-6090fc90dc49",
        order=2,
        isCompressionEnabled=False,
    )


@freeze_time("2025-07-17T12:00:00")
def test_build_location(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger, metadata=mock_metadata_cache
    )

    result = transformer.build_location(
        mock_legacy_service,
        "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
    )

    assert isinstance(result, Location)
    assert result == Location(
        id="6ef3317e-c6dc-5e27-b36d-577c375eb060",
        active=True,
        managingOrganisation="0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        address=Address(
            line1="123 Main St",
            line2=None,
            county="West Yorkshire",
            town="Leeds",
            postcode="AB12 3CD",
        ),
        name=None,
        positionGCS=PositionGCS(
            latitude="51.5074",
            longitude="-0.1278",
        ),
        primaryAddress=True,
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-17T12:00:00Z",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-17T12:00:00Z",
        partOf=None,
    )


@freeze_time("2025-07-17T12:00:00")
def test_build_location_no_position(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    mock_legacy_service.latitude = None
    mock_legacy_service.longitude = None

    transformer = BasicServiceTransformer(
        logger=mock_logger,
        metadata=mock_metadata_cache,
    )

    result = transformer.build_location(
        mock_legacy_service,
        "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
    )

    assert isinstance(result, Location)
    assert result.positionGCS is None
    assert result == Location(
        id="6ef3317e-c6dc-5e27-b36d-577c375eb060",
        active=True,
        managingOrganisation="0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        address=Address(
            line1="123 Main St",
            line2=None,
            county="West Yorkshire",
            town="Leeds",
            postcode="AB12 3CD",
        ),
        name=None,
        positionGCS=None,
        primaryAddress=True,
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-17T12:00:00Z",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-17T12:00:00Z",
        partOf=None,
    )


@freeze_time("2025-07-25T12:00:00")
def test_build_healthcare_service(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger, metadata=mock_metadata_cache
    )

    result = transformer.build_healthcare_service(
        mock_legacy_service,
        "0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        "6ef3317e-c6dc-5e27-b36d-577c375eb060",
        category="GP Services",
        type="GP Consultation Service",
    )

    assert result == HealthcareService(
        id="903cd48b-5d0f-532f-94f4-937a4517b14d",
        createdBy="DATA_MIGRATION",
        createdDateTime="2025-07-25T12:00:00+00:00",
        modifiedBy="DATA_MIGRATION",
        modifiedDateTime="2025-07-25T12:00:00+00:00",
        identifier_oldDoS_uid="test-uid",
        active=True,
        migrationNotes=None,
        category="GP Services",
        type="GP Consultation Service",
        providedBy="0fd917b6-608a-59a0-ba62-eba57ec06a0e",
        location="6ef3317e-c6dc-5e27-b36d-577c375eb060",
        name="Test Service",
        telecom=Telecom(
            phone_public="01234 567890",
            phone_private="09876 543210",
            email="firstname.lastname@nhs.net",
            web="http://example.com",
        ),
        openingTime=[
            AvailableTime(
                category="availableTime",
                dayOfWeek="mon",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="tue",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="wed",
                startTime="09:00:00",
                endTime="12:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="wed",
                startTime="13:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="thu",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="fri",
                startTime="09:00:00",
                endTime="17:00:00",
                allDay=False,
            ),
            AvailableTime(
                category="availableTime",
                dayOfWeek="sat",
                startTime="10:00:00",
                endTime="14:00:00",
                allDay=False,
            ),
            AvailableTimePublicHolidays(
                category="availableTimePublicHolidays",
                startTime="10:00:00",
                endTime="14:00:00",
            ),
        ],
        symptomGroupSymptomDiscriminators=[
            SymptomGroupSymptomDiscriminatorPair(
                sg=SymptomGroup(
                    id="2b52f7e2-c0ab-5e00-8d7d-75ede400fe7c",
                    source="pathways",
                    codeType="Symptom Group (SG)",
                    codeID=1035,
                    codeValue="Breathing Problems, Breathlessness or Wheeze, Pregnant",
                ),
                sd=SymptomDiscriminator(
                    id="300af504-ba5d-5973-a877-a0789c6863ab",
                    source="pathways",
                    codeType="Symptom Discriminator (SD)",
                    codeID=4003,
                    codeValue="PC full Primary Care assessment and prescribing capability",
                    synonyms=[],
                ),
            ),
            SymptomGroupSymptomDiscriminatorPair(
                sg=SymptomGroup(
                    id="39ce1220-2586-5b2e-a35d-3021b2e0337c",
                    source="servicefinder",
                    codeType="Symptom Group (SG)",
                    codeID=360,
                    codeValue="z2.0 - Service Types",
                ),
                sd=SymptomDiscriminator(
                    id="6ce70d41-9337-578d-a662-d9fe25016d40",
                    source="servicefinder",
                    codeType="Symptom Discriminator (SD)",
                    codeID=14023,
                    codeValue="GP Practice",
                    synonyms=["General Practice"],
                ),
            ),
        ],
        dispositions=[
            Disposition(
                id="4443b15a-26a3-517f-8a93-eb7c2539d4fc",
                source="pathways",
                codeType="Disposition (Dx)",
                codeID=126,
                codeValue="Contact Own GP Practice next working day for appointment",
                time=7200,
            ),
            Disposition(
                id="ae7a129f-cda2-51f6-aff6-88a94f7f36de",
                source="pathways",
                codeType="Disposition (Dx)",
                codeID=10,
                codeValue="Speak to a Primary Care Service within 2 hours",
                time=120,
            ),
        ],
    )


def test_build_opening_times(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger,
        metadata=mock_metadata_cache,
    )

    mock_legacy_service.scheduled_opening_times = [
        ServiceDayOpening(
            id=1,
            serviceid=1,
            dayid=1,
            day=OpeningTimeDay(id=1, name="Monday"),
            times=[
                ServiceDayOpeningTime(
                    id=1,
                    starttime=time.fromisoformat("09:00:00"),
                    endtime=time.fromisoformat("17:00:00"),
                    servicedayopeningid=1,
                )
            ],
        ),
        ServiceDayOpening(
            id=2,
            serviceid=1,
            dayid=8,
            day=OpeningTimeDay(id=8, name="BankHoliday"),
            times=[
                ServiceDayOpeningTime(
                    id=2,
                    starttime=time.fromisoformat("10:00:00"),
                    endtime=time.fromisoformat("16:00:00"),
                    servicedayopeningid=2,
                )
            ],
        ),
    ]

    mock_legacy_service.specified_opening_times = [
        ServiceSpecifiedOpeningDate(
            id=1,
            serviceid=1,
            date=date.fromisoformat("2025-07-15"),
            times=[
                ServiceSpecifiedOpeningTime(
                    id=1,
                    isclosed=False,
                    starttime=time.fromisoformat("08:00:00"),
                    endtime=time.fromisoformat("12:00:00"),
                    servicespecifiedopeningdateid=1,
                ),
                ServiceSpecifiedOpeningTime(
                    id=2,
                    isclosed=False,
                    starttime=time.fromisoformat("13:00:00"),
                    endtime=time.fromisoformat("18:00:00"),
                    servicespecifiedopeningdateid=1,
                ),
            ],
        ),
        ServiceSpecifiedOpeningDate(
            id=2,
            serviceid=1,
            date=date.fromisoformat("2025-07-16"),
            times=[
                ServiceSpecifiedOpeningTime(
                    id=3,
                    isclosed=True,
                    starttime=time.fromisoformat("00:00:00"),
                    endtime=time.fromisoformat("23:59:59"),
                    servicespecifiedopeningdateid=2,
                )
            ],
        ),
    ]

    result = transformer.build_opening_times(mock_legacy_service)

    assert isinstance(result, list)
    assert result == [
        AvailableTime(
            category="availableTime",
            dayOfWeek="mon",
            startTime=time(9, 0),
            endTime=time(17, 0),
            allDay=False,
        ),
        AvailableTimePublicHolidays(
            category="availableTimePublicHolidays",
            startTime=time(10, 0),
            endTime=time(16, 0),
        ),
        AvailableTimeVariation(
            category="availableTimeVariations",
            description=None,
            startTime=datetime(2025, 7, 15, 8, 0),
            endTime=datetime(2025, 7, 15, 12, 0),
        ),
        AvailableTimeVariation(
            category="availableTimeVariations",
            description=None,
            startTime=datetime(2025, 7, 15, 13, 0),
            endTime=datetime(2025, 7, 15, 18, 0),
        ),
        NotAvailable(
            category="notAvailable",
            description=None,
            startTime=datetime(2025, 7, 16, 0, 0),
            endTime=datetime(2025, 7, 16, 23, 59, 59),
        ),
    ]


def test_build_scheduled_opening_times(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger,
        metadata=mock_metadata_cache,
    )

    mock_legacy_service.scheduled_opening_times = [
        ServiceDayOpening(
            id=1,
            serviceid=1,
            dayid=1,
            times=[
                ServiceDayOpeningTime(
                    id=1,
                    starttime=time.fromisoformat("09:00:00"),
                    endtime=time.fromisoformat("17:00:00"),
                    servicedayopeningid=1,
                )
            ],
        ),
        ServiceDayOpening(
            id=2,
            serviceid=1,
            dayid=8,
            times=[
                ServiceDayOpeningTime(
                    id=2,
                    starttime=time.fromisoformat("10:00:00"),
                    endtime=time.fromisoformat("16:00:00"),
                    servicedayopeningid=2,
                )
            ],
        ),
    ]

    result = transformer.build_scheduled_opening_times(
        mock_legacy_service.scheduled_opening_times
    )

    assert isinstance(result, list)
    assert result == [
        AvailableTime(
            category="availableTime",
            dayOfWeek="mon",
            startTime=time(9, 0),
            endTime=time(17, 0),
            allDay=False,
        ),
        AvailableTimePublicHolidays(
            category="availableTimePublicHolidays",
            startTime=time(10, 0),
            endTime=time(16, 0),
        ),
    ]


def test_build_specified_opening_times(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger,
        metadata=mock_metadata_cache,
    )

    mock_legacy_service.specified_opening_times = [
        ServiceSpecifiedOpeningDate(
            id=1,
            serviceid=1,
            date=date.fromisoformat("2025-07-15"),
            times=[
                ServiceSpecifiedOpeningTime(
                    id=1,
                    isclosed=False,
                    starttime=time.fromisoformat("08:00:00"),
                    endtime=time.fromisoformat("12:00:00"),
                    servicespecifiedopeningdateid=1,
                ),
                ServiceSpecifiedOpeningTime(
                    id=2,
                    isclosed=False,
                    starttime=time.fromisoformat("13:00:00"),
                    endtime=time.fromisoformat("18:00:00"),
                    servicespecifiedopeningdateid=1,
                ),
            ],
        ),
        ServiceSpecifiedOpeningDate(
            id=2,
            serviceid=1,
            date=date.fromisoformat("2025-07-16"),
            times=[
                ServiceSpecifiedOpeningTime(
                    id=3,
                    isclosed=True,
                    starttime=time.fromisoformat("00:00:00"),
                    endtime=time.fromisoformat("23:59:59"),
                    servicespecifiedopeningdateid=2,
                )
            ],
        ),
    ]

    result = transformer.build_specified_opening_times(
        mock_legacy_service.specified_opening_times
    )

    assert isinstance(result, list)
    assert result == [
        AvailableTimeVariation(
            category="availableTimeVariations",
            description=None,
            startTime=datetime(2025, 7, 15, 8, 0),
            endTime=datetime(2025, 7, 15, 12, 0),
        ),
        AvailableTimeVariation(
            category="availableTimeVariations",
            description=None,
            startTime=datetime(2025, 7, 15, 13, 0),
            endTime=datetime(2025, 7, 15, 18, 0),
        ),
        NotAvailable(
            category="notAvailable",
            description=None,
            startTime=datetime(2025, 7, 16, 0, 0),
            endTime=datetime(2025, 7, 16, 23, 59, 59),
        ),
    ]


def test_build_sgsds(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger,
        metadata=mock_metadata_cache,
    )
    result = transformer.build_sgsds(mock_legacy_service)

    assert isinstance(result, list)
    assert result == [
        SymptomGroupSymptomDiscriminatorPair(
            sg=SymptomGroup(
                id="2b52f7e2-c0ab-5e00-8d7d-75ede400fe7c",
                source="pathways",
                codeType="Symptom Group (SG)",
                codeID=1035,
                codeValue="Breathing Problems, Breathlessness or Wheeze, Pregnant",
            ),
            sd=SymptomDiscriminator(
                id="300af504-ba5d-5973-a877-a0789c6863ab",
                source="pathways",
                codeType="Symptom Discriminator (SD)",
                codeID=4003,
                codeValue="PC full Primary Care assessment and prescribing capability",
                synonyms=[],
            ),
        ),
        SymptomGroupSymptomDiscriminatorPair(
            sg=SymptomGroup(
                id="39ce1220-2586-5b2e-a35d-3021b2e0337c",
                source="servicefinder",
                codeType="Symptom Group (SG)",
                codeID=360,
                codeValue="z2.0 - Service Types",
            ),
            sd=SymptomDiscriminator(
                id="6ce70d41-9337-578d-a662-d9fe25016d40",
                source="servicefinder",
                codeType="Symptom Discriminator (SD)",
                codeID=14023,
                codeValue="GP Practice",
                synonyms=["General Practice"],
            ),
        ),
    ]


def test_build_dispositions(
    mock_legacy_service: Service,
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    transformer = BasicServiceTransformer(
        logger=mock_logger,
        metadata=mock_metadata_cache,
    )
    result = transformer.build_dispositions(mock_legacy_service)

    assert isinstance(result, list)
    assert result == [
        Disposition(
            id="4443b15a-26a3-517f-8a93-eb7c2539d4fc",
            source="pathways",
            codeType="Disposition (Dx)",
            codeID=126,
            codeValue="Contact Own GP Practice next working day for appointment",
            time=7200,
        ),
        Disposition(
            id="ae7a129f-cda2-51f6-aff6-88a94f7f36de",
            source="pathways",
            codeType="Disposition (Dx)",
            codeID=10,
            codeValue="Speak to a Primary Care Service within 2 hours",
            time=120,
        ),
    ]
