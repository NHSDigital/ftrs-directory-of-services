from datetime import date, datetime, time
from decimal import Decimal
from typing import Generator
from unittest.mock import patch
from uuid import UUID

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    HealthcareService,
    HealthcareServiceTelecom,
    Location,
    Organisation,
)
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.enums import (
    EndpointBusinessScenario,
    EndpointConnectionType,
    EndpointPayloadMimeType,
    EndpointPayloadType,
    EndpointStatus,
    HealthcareServiceCategory,
    HealthcareServiceType,
    OrganisationType,
    TelecomType,
)
from ftrs_data_layer.domain.legacy import (
    Disposition,
    OpeningTimeDay,
    Service,
    ServiceDayOpening,
    ServiceDayOpeningTime,
    ServiceDisposition,
    ServiceEndpoint,
    ServiceSGSD,
    ServiceSpecifiedOpeningDate,
    ServiceSpecifiedOpeningTime,
    ServiceType,
    SymptomDiscriminator,
    SymptomDiscriminatorSynonym,
    SymptomGroup,
)
from ftrs_data_layer.domain.location import Address, PositionGCS
from ftrs_data_layer.domain.telecom import Telecom

from common.cache import DoSMetadataCache
from common.config import DatabaseConfig
from reference_data_load.config import ReferenceDataLoadConfig
from service_migration.config import DataMigrationConfig


@pytest.fixture
def mock_config() -> DataMigrationConfig:
    return DataMigrationConfig(
        db_config=DatabaseConfig.from_uri(
            "postgresql://user:password@localhost:5432/testdb"
        ),
        ENVIRONMENT="test",
        WORKSPACE="test_workspace",
        ENDPOINT_URL="http://localhost:8000",
    )


@pytest.fixture
def mock_reference_data_config() -> ReferenceDataLoadConfig:
    return ReferenceDataLoadConfig(
        db_config=DatabaseConfig.from_uri(
            "postgresql://user:password@localhost:5432/testdb"
        ),
        ENVIRONMENT="test",
        WORKSPACE="test_workspace",
        ENDPOINT_URL="http://localhost:8000",
    )


@pytest.fixture()
def mock_logger() -> Generator[MockLogger, None, None]:
    """
    Mock the logger to avoid actual logging.
    """
    mock_logger = MockLogger()

    with patch.object(Logger, "get", return_value=mock_logger):
        yield mock_logger


@pytest.fixture()
def mock_legacy_service() -> Generator[Service, None, None]:
    """
    Mock a legacy service instance.
    """
    yield Service(
        id=1,
        uid="test-uid",
        name="Test Service",
        odscode="A12345",
        isnational=None,
        openallhours=False,
        publicreferralinstructions=None,
        telephonetriagereferralinstructions=None,
        restricttoreferrals=False,
        address="123 Main St$Leeds$West Yorkshire",
        town="Leeds",
        postcode="AB12 3CD",
        easting=123456,
        northing=654321,
        publicphone="01234 567890",
        nonpublicphone="09876 543210",
        fax=None,
        email="firstname.lastname@nhs.net",
        web="http://example.com",
        createdby="test_user",
        createdtime=datetime.fromisoformat("2023-01-01T00:00:00"),
        modifiedby="test_user",
        modifiedtime=datetime.fromisoformat("2023-01-02T00:00:00"),
        lasttemplatename=None,
        lasttemplateid=None,
        typeid=100,
        parentid=None,
        subregionid=None,
        statusid=1,
        organisationid=None,
        returnifopenminutes=None,
        publicname="Public Test Service",
        latitude=Decimal("51.5074"),
        longitude=Decimal("-0.1278"),
        professionalreferralinfo=None,
        lastverified=None,
        nextverificationdue=None,
        type=ServiceType(
            id=100,
            name="GP Practice",
            nationalranking=None,
            searchcapacitystatus=None,
            capacitymodel=None,
            capacityreset=None,
        ),
        endpoints=[
            ServiceEndpoint(
                id=1,
                serviceid=1,
                endpointorder=1,
                transport="http",
                interaction="urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
                businessscenario="Primary",
                address="http://example.com/endpoint",
                comment="Test Endpoint",
                iscompressionenabled="compressed",
            ),
            ServiceEndpoint(
                id=2,
                serviceid=1,
                endpointorder=2,
                transport="email",
                interaction="urn:nhs-itk:interaction:primaryOutofHourRecipientNHS111CDADocument-v2-0",
                businessscenario="Copy",
                address="mailto:test@example.com",
                comment="Test Email Endpoint",
                iscompressionenabled="uncompressed",
            ),
        ],
        scheduled_opening_times=[
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
                dayid=2,
                day=OpeningTimeDay(id=2, name="Tuesday"),
                times=[
                    ServiceDayOpeningTime(
                        id=2,
                        starttime=time.fromisoformat("09:00:00"),
                        endtime=time.fromisoformat("17:00:00"),
                        servicedayopeningid=2,
                    )
                ],
            ),
            ServiceDayOpening(
                id=3,
                serviceid=1,
                dayid=3,
                day=OpeningTimeDay(id=3, name="Wednesday"),
                times=[
                    ServiceDayOpeningTime(
                        id=3,
                        starttime=time.fromisoformat("09:00:00"),
                        endtime=time.fromisoformat("12:00:00"),
                        servicedayopeningid=3,
                    ),
                    ServiceDayOpeningTime(
                        id=4,
                        starttime=time.fromisoformat("13:00:00"),
                        endtime=time.fromisoformat("17:00:00"),
                        servicedayopeningid=3,
                    ),
                ],
            ),
            ServiceDayOpening(
                id=4,
                serviceid=1,
                dayid=4,
                day=OpeningTimeDay(id=4, name="Thursday"),
                times=[
                    ServiceDayOpeningTime(
                        id=5,
                        starttime=time.fromisoformat("09:00:00"),
                        endtime=time.fromisoformat("17:00:00"),
                        servicedayopeningid=4,
                    )
                ],
            ),
            ServiceDayOpening(
                id=5,
                serviceid=1,
                dayid=5,
                day=OpeningTimeDay(id=5, name="Friday"),
                times=[
                    ServiceDayOpeningTime(
                        id=6,
                        starttime=time.fromisoformat("09:00:00"),
                        endtime=time.fromisoformat("17:00:00"),
                        servicedayopeningid=5,
                    )
                ],
            ),
            ServiceDayOpening(
                id=6,
                serviceid=1,
                dayid=6,
                day=OpeningTimeDay(id=6, name="Saturday"),
                times=[
                    ServiceDayOpeningTime(
                        id=7,
                        starttime=time.fromisoformat("10:00:00"),
                        endtime=time.fromisoformat("14:00:00"),
                        servicedayopeningid=6,
                    )
                ],
            ),
            ServiceDayOpening(
                id=7,
                serviceid=1,
                dayid=8,
                day=OpeningTimeDay(id=8, name="BankHoliday"),
                times=[
                    ServiceDayOpeningTime(
                        id=8,
                        starttime=time.fromisoformat("10:00:00"),
                        endtime=time.fromisoformat("14:00:00"),
                        servicedayopeningid=7,
                    )
                ],
            ),
        ],
        specified_opening_dates=[
            ServiceSpecifiedOpeningDate(
                id=1,
                serviceid=1,
                date=date.fromisoformat("2023-01-01"),
                times=[
                    ServiceSpecifiedOpeningTime(
                        id=1,
                        starttime=time.fromisoformat("10:00:00"),
                        endtime=time.fromisoformat("14:00:00"),
                        isclosed=False,
                        servicespecifiedopeningdateid=1,
                    )
                ],
            ),
            ServiceSpecifiedOpeningDate(
                id=2,
                serviceid=1,
                date=date.fromisoformat("2023-01-02"),
                times=[
                    ServiceSpecifiedOpeningTime(
                        id=2,
                        starttime=time.fromisoformat("00:00:00"),
                        endtime=time.fromisoformat("23:59:59"),
                        isclosed=True,
                        servicespecifiedopeningdateid=2,
                    )
                ],
            ),
        ],
        sgsds=[
            ServiceSGSD(
                id=1,
                sgid=1035,
                sdid=4003,
                group=SymptomGroup(
                    name="Breathing Problems, Breathlessness or Wheeze, Pregnant",
                    id=1035,
                    zcodeexists=None,
                ),
                discriminator=SymptomDiscriminator(
                    id=4003,
                    description="PC full Primary Care assessment and prescribing capability",
                    synonyms=[],
                ),
            ),
            ServiceSGSD(
                id=2,
                sgid=360,
                sdid=14023,
                group=SymptomGroup(
                    id=360, name="z2.0 - Service Types", zcodeexists=True
                ),
                discriminator=SymptomDiscriminator(
                    id=14023,
                    description="GP Practice",
                    synonyms=[
                        SymptomDiscriminatorSynonym(
                            id=2341,
                            symptomdiscriminatorid=14023,
                            name="General Practice",
                        )
                    ],
                ),
            ),
        ],
        dispositions=[
            ServiceDisposition(
                id=1,
                serviceid=1,
                dispositionid=126,
                disposition=Disposition(
                    id=126,
                    name="Contact Own GP Practice next working day for appointment",
                    dxcode="DX115",
                    dispositiontime=7200,
                ),
            ),
            ServiceDisposition(
                id=2,
                serviceid=1,
                dispositionid=10,
                disposition=Disposition(
                    id=10,
                    name="Speak to a Primary Care Service within 2 hours",
                    dxcode="DX12",
                    dispositiontime=120,
                ),
            ),
        ],
    )


@pytest.fixture
def mock_metadata_cache(mock_config: DataMigrationConfig) -> DoSMetadataCache:
    """
    Mock a metadata cache instance.
    """
    cache = DoSMetadataCache(None)
    cache.symptom_groups.cache = {
        1035: SymptomGroup(
            id=1035,
            name="Breathing Problems, Breathlessness or Wheeze, Pregnant",
            zcodeexists=None,
        ),
        360: SymptomGroup(id=360, name="z2.0 - Service Types", zcodeexists=True),
    }
    cache.symptom_discriminators.cache = {
        4003: SymptomDiscriminator(
            id=4003,
            description="PC full Primary Care assessment and prescribing capability",
            synonyms=[],
        ),
        14023: SymptomDiscriminator(
            id=14023,
            description="GP Practice",
            synonyms=[
                SymptomDiscriminatorSynonym(
                    id=2341, symptomdiscriminatorid=14023, name="General Practice"
                )
            ],
        ),
    }
    cache.dispositions.cache = {
        126: Disposition(
            id=126,
            name="Contact Own GP Practice next working day for appointment",
            dxcode="DX115",
            dispositiontime=7200,
        ),
        10: Disposition(
            id=10,
            name="Speak to a Primary Care Service within 2 hours",
            dxcode="DX12",
            dispositiontime=120,
        ),
    }
    cache.opening_time_days.cache = {
        1: OpeningTimeDay(id=1, name="Monday"),
        2: OpeningTimeDay(id=2, name="Tuesday"),
        3: OpeningTimeDay(id=3, name="Wednesday"),
        4: OpeningTimeDay(id=4, name="Thursday"),
        5: OpeningTimeDay(id=5, name="Friday"),
        6: OpeningTimeDay(id=6, name="Saturday"),
        7: OpeningTimeDay(id=7, name="Sunday"),
        8: OpeningTimeDay(id=8, name="BankHoliday"),
    }
    cache.service_types.cache = {
        100: ServiceType(
            id=100,
            name="GP Practice",
            nationalranking=None,
            searchcapacitystatus=None,
            capacitymodel=None,
            capacityreset=None,
        ),
        136: ServiceType(
            id=136,
            name="GP Access Hub",
            nationalranking=None,
            searchcapacitystatus=None,
            capacitymodel=None,
            capacityreset=None,
        ),
        152: ServiceType(
            id=152,
            name="Primary Care Network (PCN) Enhanced Service",
            nationalranking=None,
            searchcapacitystatus=None,
            capacitymodel=None,
            capacityreset=None,
        ),
    }

    with patch("common.cache.DoSMetadataCache") as mock_cache:
        mock_cache.return_value = cache
        yield cache


@pytest.fixture
def mock_lambda_context() -> LambdaContext:
    """
    Mock the Lambda context for testing.
    """
    context = LambdaContext()
    context._function_name = "test_lambda_function"
    context._function_version = "$LATEST"
    context._invoked_function_arn = "invoked-function-arn"
    context._aws_request_id = "mock-request-id"
    context._log_group_name = "/aws/lambda/test_lambda_function"
    context._log_stream_name = "log-stream-name"
    context._memory_limit_in_mb = 1024
    return context


@pytest.fixture
def base_organisation() -> Organisation:
    return Organisation(
        id=UUID("4ebead71-69d6-4571-8cff-982c54047903"),
        identifier_oldDoS_uid="UID123",
        identifier_ODS_ODSCode="ODS001",
        active=True,
        name="Test Organisation",
        type=OrganisationType.GP_PRACTICE,
        telecom=[
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True),
        ],
        endpoints=[],
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime(2023, 1, 1),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime(2023, 2, 1),
    )


@pytest.fixture
def base_location() -> Location:
    return Location(
        id=UUID("34316f80-0b96-48f3-ae07-f70288637fb5"),
        identifier_oldDoS_uid="LOC123",
        active=True,
        address=Address(
            line1="123 Test Street",
            line2="Test Area",
            county="Test County",
            town="Test Town",
            postcode="TE1 1ST",
        ),
        managingOrganisation=UUID("4ebead71-69d6-4571-8cff-982c54047903"),
        name="Test Location",
        positionGCS=PositionGCS(
            latitude=Decimal("51.5074"), longitude=Decimal("-0.1278")
        ),
        primaryAddress=True,
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime(2023, 1, 1),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime(2023, 1, 1),
    )


@pytest.fixture
def base_healthcare_service() -> HealthcareService:
    return HealthcareService(
        id=UUID("43f8c8c0-2272-4371-966a-f2db6d338e58"),
        identifier_oldDoS_uid="HS123",
        active=True,
        category=HealthcareServiceCategory.GP_SERVICES,
        type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
        providedBy=UUID("4ebead71-69d6-4571-8cff-982c54047903"),
        location=UUID("34316f80-0b96-48f3-ae07-f70288637fb5"),
        name="Test Healthcare Service",
        telecom=HealthcareServiceTelecom(
            phone_public="0123456789",
            phone_private="9876543210",
            email="test@example.com",
            web="https://www.example.com",
        ),
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime(2023, 1, 1),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime(2023, 1, 1),
    )


@pytest.fixture
def base_endpoint() -> Endpoint:
    return Endpoint(
        id=UUID("aaceeace-0cb7-46df-89d9-ca8cd3cbc843"),
        identifier_oldDoS_id=123,
        status=EndpointStatus.ACTIVE,
        connectionType=EndpointConnectionType.ITK,
        name="Test Endpoint",
        businessScenario=EndpointBusinessScenario.PRIMARY,
        payloadType=EndpointPayloadType.GP_PRIMARY,
        payloadMimeType=EndpointPayloadMimeType.CDA,
        address="https://test.endpoint.com",
        managedByOrganisation=UUID("4ebead71-69d6-4571-8cff-982c54047903"),
        service=UUID("43f8c8c0-2272-4371-966a-f2db6d338e58"),
        order=1,
        isCompressionEnabled=False,
        createdBy={"display": "Test User", "type": "app", "value": "TESTVALUE"},
        createdTime=datetime(2023, 1, 1),
        lastUpdatedBy={"display": "Test User12", "type": "app", "value": "TESTVALUE"},
        lastUpdated=datetime(2023, 1, 1),
    )
