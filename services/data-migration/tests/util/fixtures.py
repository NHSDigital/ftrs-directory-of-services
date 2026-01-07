import re
from contextlib import contextmanager
from datetime import date, datetime, time
from decimal import Decimal
from typing import Generator
from unittest.mock import MagicMock, patch

import boto3
import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain.legacy.data_models import (
    ServiceData,
    ServiceDayOpeningData,
    ServiceDayOpeningTimeData,
    ServiceDispositionData,
    ServiceEndpointData,
    ServiceSGSDData,
    ServiceSpecifiedOpeningDateData,
    ServiceSpecifiedOpeningTimeData,
)
from ftrs_data_layer.domain.legacy.db_models import (
    Disposition,
    OpeningTimeDay,
    Service,
    ServiceType,
    SymptomDiscriminator,
    SymptomDiscriminatorSynonym,
    SymptomGroup,
)
from moto import mock_aws
from mypy_boto3_dynamodb import DynamoDBClient
from pytest_mock import MockerFixture
from sqlalchemy import Engine, Executable, create_mock_engine

from common.cache import DoSMetadataCache
from common.config import DatabaseConfig
from reference_data_load.config import ReferenceDataLoadConfig
from service_migration.config import ServiceMigrationConfig
from service_migration.dependencies import ServiceMigrationDependencies


@pytest.fixture
def mock_config() -> ServiceMigrationConfig:
    return ServiceMigrationConfig(
        db_config=DatabaseConfig.from_uri(
            "postgresql://user:password@localhost:5432/testdb"
        ),
        ENVIRONMENT="local",
        WORKSPACE="test-workspace",
        ENDPOINT_URL="http://localhost:8000",
    )


@pytest.fixture
def mock_reference_data_config() -> ReferenceDataLoadConfig:
    return ReferenceDataLoadConfig(
        db_config=DatabaseConfig.from_uri(
            "postgresql://user:password@localhost:5432/testdb"
        ),
        ENVIRONMENT="local",
        WORKSPACE="test-workspace",
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
def mock_legacy_service() -> Generator[ServiceData, None, None]:
    """
    Mock a legacy service instance.
    """
    yield ServiceData(
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
        endpoints=[
            ServiceEndpointData(
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
            ServiceEndpointData(
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
                dayid=2,
                times=[
                    ServiceDayOpeningTimeData(
                        id=2,
                        starttime=time.fromisoformat("09:00:00"),
                        endtime=time.fromisoformat("17:00:00"),
                        servicedayopeningid=2,
                    )
                ],
            ),
            ServiceDayOpeningData(
                id=3,
                serviceid=1,
                dayid=3,
                times=[
                    ServiceDayOpeningTimeData(
                        id=3,
                        starttime=time.fromisoformat("09:00:00"),
                        endtime=time.fromisoformat("12:00:00"),
                        servicedayopeningid=3,
                    ),
                    ServiceDayOpeningTimeData(
                        id=4,
                        starttime=time.fromisoformat("13:00:00"),
                        endtime=time.fromisoformat("17:00:00"),
                        servicedayopeningid=3,
                    ),
                ],
            ),
            ServiceDayOpeningData(
                id=4,
                serviceid=1,
                dayid=4,
                times=[
                    ServiceDayOpeningTimeData(
                        id=5,
                        starttime=time.fromisoformat("09:00:00"),
                        endtime=time.fromisoformat("17:00:00"),
                        servicedayopeningid=4,
                    )
                ],
            ),
            ServiceDayOpeningData(
                id=5,
                serviceid=1,
                dayid=5,
                times=[
                    ServiceDayOpeningTimeData(
                        id=6,
                        starttime=time.fromisoformat("09:00:00"),
                        endtime=time.fromisoformat("17:00:00"),
                        servicedayopeningid=5,
                    )
                ],
            ),
            ServiceDayOpeningData(
                id=6,
                serviceid=1,
                dayid=6,
                times=[
                    ServiceDayOpeningTimeData(
                        id=7,
                        starttime=time.fromisoformat("10:00:00"),
                        endtime=time.fromisoformat("14:00:00"),
                        servicedayopeningid=6,
                    )
                ],
            ),
            ServiceDayOpeningData(
                id=7,
                serviceid=1,
                dayid=8,
                times=[
                    ServiceDayOpeningTimeData(
                        id=8,
                        starttime=time.fromisoformat("10:00:00"),
                        endtime=time.fromisoformat("14:00:00"),
                        servicedayopeningid=7,
                    )
                ],
            ),
        ],
        specified_opening_times=[
            ServiceSpecifiedOpeningDateData(
                id=1,
                serviceid=1,
                date=date.fromisoformat("2023-01-01"),
                times=[
                    ServiceSpecifiedOpeningTimeData(
                        id=1,
                        starttime=time.fromisoformat("10:00:00"),
                        endtime=time.fromisoformat("14:00:00"),
                        isclosed=False,
                        servicespecifiedopeningdateid=1,
                    )
                ],
            ),
            ServiceSpecifiedOpeningDateData(
                id=2,
                serviceid=1,
                date=date.fromisoformat("2023-01-02"),
                times=[
                    ServiceSpecifiedOpeningTimeData(
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
            ServiceSGSDData(
                id=1,
                sgid=1035,
                sdid=4003,
                serviceid=1,
            ),
            ServiceSGSDData(
                id=2,
                sgid=360,
                sdid=14023,
                serviceid=1,
            ),
        ],
        dispositions=[
            ServiceDispositionData(
                id=1,
                serviceid=1,
                dispositionid=126,
            ),
            ServiceDispositionData(
                id=2,
                serviceid=1,
                dispositionid=10,
            ),
        ],
        age_range=[],
    )


SERVICE_BY_ID_REGEX = re.compile(
    r"^SELECT pathwaysdos\.services.*\nFROM pathwaysdos.services.*?\nWHERE pathwaysdos.services.id = (\d)*?$"
)


@pytest.fixture(scope="function")
def stub_test_services() -> dict[int, Service]:
    """
    Stub test services for database queries.
    """
    return {
        1: Service(
            id=1,
            uid="2000000001",
            name="Test Service 1",
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
            email="test@nhs.net",
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
            publicname="Public Test Service 1",
            latitude=Decimal("51.5074"),
            longitude=Decimal("-0.1278"),
            professionalreferralinfo=None,
            lastverified=None,
            nextverificationdue=None,
            endpoints=[],
            scheduled_opening_times=[],
            specified_opening_times=[],
            sgsds=[],
            dispositions=[],
        )
    }


@pytest.fixture
def mock_db_engine(
    mocker: MockerFixture, stub_test_services: dict[int, Service]
) -> Generator[Engine, None, None]:
    """
    Mock a database engine for testing.
    """

    def mock_executor(sql: Executable, *args: object) -> MagicMock:
        compiled = sql.compile(compile_kwargs={"literal_binds": True})
        if match := SERVICE_BY_ID_REGEX.match(compiled.string):
            service_id = int(match.group(1))
            service = stub_test_services.get(service_id)

            mock_result = mocker.MagicMock()
            mock_result.scalars.return_value.unique.return_value.one_or_none.return_value = service

            return mock_result

        raise ValueError(f"Unrecognized SQL: {compiled.string}")

    engine = create_mock_engine("sqlite://", executor=mock_executor)

    @contextmanager
    def begin() -> Generator[Engine, None, None]:
        yield engine

    engine.begin = begin
    engine.close = lambda: None

    session_mock = mocker.patch("service_migration.processor.Session")
    session_mock.return_value.__enter__.return_value.execute.side_effect = mock_executor
    yield engine


@pytest.fixture(scope="function")
def mock_dynamodb_client(
    mock_config: ServiceMigrationConfig,
) -> Generator[DynamoDBClient, None, None]:
    """
    Mock a DynamoDB client for testing.
    """
    with mock_aws():
        dynamodb_client = boto3.client(
            "dynamodb", aws_access_key_id="test", aws_secret_access_key="test"
        )

        dynamodb_client.create_table(
            TableName="ftrs-dos-local-data-migration-state-table-test-workspace",
            KeySchema=[
                {"AttributeName": "source_record_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "source_record_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        dynamodb_client.create_table(
            TableName="ftrs-dos-local-database-organisation-test-workspace",
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        dynamodb_client.create_table(
            TableName="ftrs-dos-local-database-location-test-workspace",
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        dynamodb_client.create_table(
            TableName="ftrs-dos-local-database-healthcare-service-test-workspace",
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        yield dynamodb_client


@pytest.fixture
def mock_dependencies(
    mock_config: ServiceMigrationConfig,
    mock_logger: MockLogger,
    mock_metadata_cache: DoSMetadataCache,
    mock_db_engine: Engine,
    mock_dynamodb_client: DynamoDBClient,
) -> Generator[None, None, None]:
    """
    Mock dependencies for service migration tests.
    """
    dependencies = ServiceMigrationDependencies(
        config=mock_config,
        logger=mock_logger,
        engine=mock_db_engine,
        metadata=mock_metadata_cache,
        ddb_client=mock_dynamodb_client,
    )
    yield dependencies


@pytest.fixture
def mock_metadata_cache(
    mock_config: ServiceMigrationConfig,
) -> Generator[DoSMetadataCache, None, None]:
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
