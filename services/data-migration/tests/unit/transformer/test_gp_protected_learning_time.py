from uuid import UUID

import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)
from ftrs_data_layer.domain.legacy import Service
from ftrs_data_layer.domain.legacy.service import ServiceSGSD

from pipeline.transformer.gp_protected_learning_time import (
    GPProtectedLearningTimeTransformer,
)
from pipeline.utils.cache import DoSMetadataCache


@pytest.mark.parametrize(
    "test_data",
    [
        # Invalid service type
        {
            "service_type_id": 200,  # invalid service type
            "ods_code": "A12345",
            "name": "PLT - GP COVER",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "Service typeid 200 is not supported",
        },
        # Invalid ODS code
        {
            "service_type_id": 100,
            "ods_code": None,
            "name": "Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "Service does not have an ODS code",
            # no ODS Code
        },
        {
            "service_type_id": 100,
            "ods_code": "q12345",
            "name": "Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (full length)",
            # lower case letter
        },
        {
            "service_type_id": 100,
            "ods_code": "AB12345",
            "name": "Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (full length)",
            # start with 2 letters
        },
        {
            "service_type_id": 100,
            "ods_code": "A1234",
            "name": "Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (full length)",
            # only 4 digits
        },
        {
            "service_type_id": 100,
            "ods_code": "A123456789",
            "name": "Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (full length)",
            # 9 digits
        },
        {
            "service_type_id": 100,
            "ods_code": "A12345A",
            "name": "Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (full length)",
            # ends with letter
        },
        {
            "service_type_id": 100,
            "ods_code": "12345A",
            "name": "Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (full length)",
            # starts with no letter
        },
        # Invalid name
        {
            "service_type_id": 200,
            "ods_code": "H98765",
            "name": "Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "Service typeid 200 is not supported",
            # with invalid service type
        },
        {
            "service_type_id": 100,
            "ods_code": "A12345",
            "name": "Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "Service name does not contain 'PLT' or 'GP Cover'",
        },  # with valid service type (GP Practice)
        {
            "service_type_id": 136,
            "ods_code": "A12345",
            "name": "Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "Service name does not contain 'PLT' or 'GP Cover'",
        },  # with valid service type (GP Access Hub)
        {
            "service_type_id": 159,
            "ods_code": "A12345",
            "name": "Name",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "postcode": "A01 2BC",
            "expected_result": False,
            "expected_message": "Service name does not contain 'PLT' or 'GP Cover'",
        },  # with valid service type (Primary Care Clinic)
        # Invalid postcode or SG code
        {
            "service_type_id": 100,
            "ods_code": "G123456",
            "name": "PLT - GP COVER",
            "postcode": None,  # no postcode
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": False,
            "expected_message": "Profile must be linked to at least 1 SG code or contain a postcode",
        },
        {
            "service_type_id": 100,
            "ods_code": "G123456",
            "name": "PLT - GP COVER",
            "postcode": "A01 2BC",
            "sgsds": [],  # no SG code
            "expected_result": False,
            "expected_message": "Profile must be linked to at least 1 SG code or contain a postcode",
        },
        {
            "service_type_id": 100,
            "ods_code": "G123456",
            "name": "PLT - GP COVER",
            "postcode": None,  # no postcode
            "sgsds": [],  # no SG code
            "expected_result": False,
            "expected_message": "Profile must be linked to at least 1 SG code or contain a postcode",
        },
    ],
)
def test_is_service_supported_invalid_services(
    mock_legacy_service: Service,
    test_data: dict,
) -> None:
    """
    Test that is_service_supported returns True for a valid GP profile
    """
    mock_legacy_service.typeid = test_data["service_type_id"]
    mock_legacy_service.odscode = test_data["ods_code"]
    mock_legacy_service.name = test_data["name"]
    mock_legacy_service.postcode = test_data["postcode"]
    mock_legacy_service.sgsds = test_data["sgsds"]

    is_supported, message = GPProtectedLearningTimeTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == test_data["expected_result"]
    assert message == test_data["expected_message"]


@pytest.mark.parametrize(
    "test_data",
    [
        # Valid GP Protected Learning Time Services
        {
            "service_type_id": 100,  # GP Practice
            "ods_code": "G123456",
            "name": "PLT - GP COVER",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": True,
            "expected_message": None,
        },  # both PLT and GP Cover
        {
            "service_type_id": 136,  # GP Access Hub
            "ods_code": "G123456",
            "name": "PLT - GP COVER",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": True,
            "expected_message": None,
        },  # both PLT and GP Cover
        {
            "service_type_id": 159,  # Primary Care Clinic
            "ods_code": "G123456",
            "name": "PLT - GP COVER",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": True,
            "expected_message": None,
        },  # both PLT and GP Cover
        {
            "service_type_id": 100,
            "ods_code": "H98765",
            "name": "PLT - Name",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": True,
            "expected_message": None,
        },  # only PLT
        {
            "service_type_id": 136,
            "ods_code": "H98765",
            "name": "Name - GP Cover",
            "postcode": "A01 2BC",
            "sgsds": [ServiceSGSD(id=1, serviceid=1, sdid=101, sgid=201)],
            "expected_result": True,
            "expected_message": None,
        },  # only GP Cover
    ],
)
def test_is_service_supported_valid_services(
    mock_legacy_service: Service,
    test_data: dict,
) -> None:
    """
    Test that is_service_supported returns True for a valid GP profile
    """
    mock_legacy_service.typeid = test_data["service_type_id"]
    mock_legacy_service.odscode = test_data["ods_code"]
    mock_legacy_service.name = test_data["name"]
    mock_legacy_service.postcode = test_data["postcode"]
    mock_legacy_service.sgsds = test_data["sgsds"]

    is_supported, message = GPProtectedLearningTimeTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == test_data["expected_result"]
    assert message == test_data["expected_message"]


@pytest.mark.parametrize(
    "status_id, expected_result, expected_message",
    [
        (1, True, None),  # Active service
        (2, False, "Service is not 'active' or 'commissioning'"),
        (3, True, None),  # Commissioning service
    ],
)
def test_should_include_service(
    mock_legacy_service: Service,
    status_id: int,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    """
    Test that should_include_service returns True for a valid GP Protected Learning Time Service
    """
    mock_legacy_service.typeid = 100  # GP Practice type ID
    mock_legacy_service.odscode = "A12345"  # Valid ODS code
    mock_legacy_service.statusid = status_id

    should_include, message = GPProtectedLearningTimeTransformer.should_include_service(
        mock_legacy_service
    )

    assert should_include == expected_result
    assert message == expected_message


def test_transform(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mock_logger: MockLogger,
) -> None:
    """
    Test that transform method correctly transforms a GP Protected Learning Time Service
    """
    transformer = GPProtectedLearningTimeTransformer(mock_logger, mock_metadata_cache)

    mock_legacy_service.uid = "903cd48b-5d0f-532f-94f4-937a4517b14d"
    result = transformer.transform(mock_legacy_service)

    assert len(result.organisation) == 0
    assert len(result.location) == 0
    assert len(result.healthcare_service) == 1
    assert (
        result.healthcare_service[0].category == HealthcareServiceCategory.GP_SERVICES
    )
    assert result.healthcare_service[0].type == HealthcareServiceType.PLT_SERVICE

    assert mock_logger.get_log("DM_ETL_017") == [
        {
            "msg": "Healthcare service has opening times with service id: 903cd48b-5d0f-532f-94f4-937a4517b14d",
            "reference": "DM_ETL_017",
            "detail": {"service_id": UUID("903cd48b-5d0f-532f-94f4-937a4517b14d")},
        }
    ]
