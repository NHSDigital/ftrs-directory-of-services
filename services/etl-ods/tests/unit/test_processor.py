import json
from datetime import datetime
from typing import Generator, NamedTuple

import pytest
from ftrs_common.utils.correlation_id import set_correlation_id
from ftrs_common.utils.request_id import set_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock
from requests_mock.adapter import _Matcher as Matcher

from producer.processor import (
    processor,
)

TEST_CORRELATION_ID = "test-correlation"
TEST_REQUEST_ID = "test-request"


@pytest.fixture(autouse=True)
def fixed_ids() -> Generator[None, None, None]:
    set_correlation_id(TEST_CORRELATION_ID)
    set_request_id(TEST_REQUEST_ID)
    yield
    set_correlation_id(None)
    set_request_id(None)


class MockResponses(NamedTuple):
    ods_api: Matcher
    apim_org_abc123: Matcher


# Helper functions to reduce duplication
def _helper_create_organization_resource(ods_code: str) -> dict:
    return {
        "resourceType": "Organization",
        "id": ods_code,
        "name": f"Test Organisation {ods_code} ODS",
        "active": True,
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": ods_code,
            }
        ],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "instanceID",
                        "valueInteger": 78491,
                    },
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                    "display": "PRESCRIBING COST CENTRE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {
                                    "start": "1974-04-01",
                                },
                            },
                        ],
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Operational",
                                    "display": "Operational",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {
                                    "start": "1974-04-01",
                                },
                            },
                        ],
                    },
                    {
                        "url": "active",
                        "valueBoolean": True,
                    },
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "instanceID",
                        "valueInteger": 195368,
                    },
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO76",
                                    "display": "GP PRACTICE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {
                                    "start": "2014-04-15",
                                },
                            },
                        ],
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Operational",
                                    "display": "Operational",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {
                                    "start": "2014-04-15",
                                },
                            },
                        ],
                    },
                    {
                        "url": "active",
                        "valueBoolean": True,
                    },
                ],
            },
        ],
    }


def create_ods_terminology_bundle(organizations: list[dict]) -> dict:
    """Create a FHIR Bundle response from ODS Terminology API."""
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(organizations),
        "status_code": 200,
        "entry": [{"resource": org} for org in organizations],
    }


def create_apim_uuid_bundle(uuid: str) -> dict:
    """Create a FHIR Bundle response for APIM UUID lookup."""
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "status_code": 200,
        "entry": [
            {
                "resource": {
                    "resourceType": "Organization",
                    "id": uuid,
                }
            }
        ],
    }


@pytest.fixture
def mock_responses(requests_mock: RequestsMock) -> MockResponses:
    """Setup standard mock responses for ODS Terminology API and APIM."""
    org_abc123 = _helper_create_organization_resource("ABC123")
    ods_terminology_bundle = create_ods_terminology_bundle([org_abc123])

    ods_api_mock = requests_mock.get(
        "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        json=ods_terminology_bundle,
    )

    # Setup APIM API Mock for Organisation UUID
    apim_bundle = create_apim_uuid_bundle("00000000-0000-0000-0000-000000000abc")
    apim_org_abc123_mock = requests_mock.get(
        "http://test-apim-api/Organization?identifier=odsOrganisationCode|ABC123",
        json=apim_bundle,
    )

    return MockResponses(
        ods_api=ods_api_mock,
        apim_org_abc123=apim_org_abc123_mock,
    )


def test_processor_processing_organisations_successful(
    mocker: MockerFixture,
    requests_mock: RequestsMock,
    mock_responses: MockResponses,
) -> None:
    expected_call_count = 2  # ODS Terminology API + APIM UUID lookup
    date = datetime.now().strftime("%Y-%m-%d")
    load_data_mock = mocker.patch("producer.processor.load_data")
    assert processor(date) is None
    assert requests_mock.call_count == expected_call_count

    # Assert ODS Terminology API Call
    assert mock_responses.ods_api.called_once
    assert mock_responses.ods_api.last_request.qs == {
        "_lastupdated": [date],
        "_count": ["1000"],
    }
    assert requests_mock.request_history[0] == mock_responses.ods_api.last_request

    # Assert APIM API Call for Organisation UUID
    assert mock_responses.apim_org_abc123.called_once
    assert mock_responses.apim_org_abc123.last_request.path == "/organization"
    assert (
        mock_responses.apim_org_abc123.last_request.query
        == "identifier=odsorganisationcode%7cabc123"
    )
    assert (
        requests_mock.request_history[1] == mock_responses.apim_org_abc123.last_request
    )
    # Assert load_data call
    load_data_mock.assert_called_once()
    data_to_load = [json.loads(entry) for entry in load_data_mock.call_args[0][0]]
    # Check the data struct
    assert data_to_load == [
        {
            "path": "00000000-0000-0000-0000-000000000abc",
            "body": {
                "resourceType": "Organization",
                "id": "00000000-0000-0000-0000-000000000abc",
                "meta": {
                    "profile": [
                        "https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"
                    ]
                },
                "active": True,
                "type": [
                    {
                        "coding": [
                            {
                                "system": "TO-DO",
                                "code": "GP Practice",
                                "display": "GP Practice",
                            }
                        ],
                        "text": "GP Practice",
                    }
                ],
                "name": "Test Organisation ABC123 ODS",
                "identifier": [
                    {
                        "use": "official",
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "ABC123",
                    }
                ],
                "telecom": [],
                "extension": [
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                        "extension": [
                            {
                                "url": "instanceID",
                                "valueInteger": 78491,
                            },
                            {
                                "url": "roleCode",
                                "valueCodeableConcept": {
                                    "coding": [
                                        {
                                            "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                            "code": "RO177",
                                            "display": "PRESCRIBING COST CENTRE",
                                        }
                                    ]
                                },
                            },
                            {
                                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                                "extension": [
                                    {
                                        "url": "dateType",
                                        "valueCoding": {
                                            "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                            "code": "Legal",
                                            "display": "Legal",
                                        },
                                    },
                                    {
                                        "url": "period",
                                        "valuePeriod": {
                                            "start": "1974-04-01",
                                        },
                                    },
                                ],
                            },
                            {
                                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                                "extension": [
                                    {
                                        "url": "dateType",
                                        "valueCoding": {
                                            "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                            "code": "Operational",
                                            "display": "Operational",
                                        },
                                    },
                                    {
                                        "url": "period",
                                        "valuePeriod": {
                                            "start": "1974-04-01",
                                        },
                                    },
                                ],
                            },
                            {
                                "url": "active",
                                "valueBoolean": True,
                            },
                        ],
                    }
                ],
            },
            "correlation_id": TEST_CORRELATION_ID,
            "request_id": TEST_REQUEST_ID,
        }
    ]


def test_processor_continue_on_validation_failure(
    mocker: MockerFixture,
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that processing continues when one organization fails validation."""
    org_abc123 = _helper_create_organization_resource("ABC123")
    org_efg456 = _helper_create_organization_resource("EFG456")
    ods_terminology_bundle = create_ods_terminology_bundle([org_abc123, org_efg456])

    ods_api_mock = requests_mock.get(
        "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        json=ods_terminology_bundle,
    )

    # ABC123 fails UUID lookup
    apim_api_abc123_mock = requests_mock.get(
        "http://test-apim-api/Organization?identifier=odsOrganisationCode|ABC123",
        status_code=422,  # Simulate Unprocessable Entity error
    )

    # EFG456 succeeds
    apim_bundle_efg456 = create_apim_uuid_bundle("00000000-0000-0000-0000-000000000EFG")
    apim_efg456_mock = requests_mock.get(
        "http://test-apim-api/Organization?identifier=odsOrganisationCode|EFG456",
        json=apim_bundle_efg456,
    )
    expected_call_count = (
        3  # ODS Terminology API + 2 APIM UUID lookups (ABC123 fails, EFG456 succeeds)
    )

    date = datetime.now().strftime("%Y-%m-%d")

    load_data_mock = mocker.patch("producer.processor.load_data")
    assert processor(date) is None

    assert requests_mock.call_count == expected_call_count
    # Assert ODS Terminology API Call
    assert ods_api_mock.called_once
    assert ods_api_mock.last_request.qs == {"_lastupdated": [date], "_count": ["1000"]}
    assert requests_mock.request_history[0] == ods_api_mock.last_request

    # Assert APIM API Call for ABC123 UUID (fails)
    assert apim_api_abc123_mock.called_once
    assert (
        apim_api_abc123_mock.last_request.query
        == "identifier=odsorganisationcode%7cabc123"
    )

    assert requests_mock.request_history[1] == apim_api_abc123_mock.last_request

    # Failure for ABC123 should be logged
    assert "422 Client Error" in caplog.text

    # Assert APIM API Call for EFG456 UUID (succeeds)
    assert apim_efg456_mock.called_once
    assert apim_efg456_mock.last_request.path == "/organization"
    assert (
        apim_efg456_mock.last_request.query == "identifier=odsorganisationcode%7cefg456"
    )
    assert requests_mock.request_history[2] == apim_efg456_mock.last_request

    # Assert load_data call - only EFG456 should be loaded
    load_data_mock.assert_called_once()
    data_to_load = [json.loads(entry) for entry in load_data_mock.call_args[0][0]]

    assert len(data_to_load) == 1
    assert data_to_load[0]["path"] == "00000000-0000-0000-0000-000000000EFG"
    assert data_to_load[0]["body"]["identifier"][0]["value"] == "EFG456"


def test_processor_no_outdated_organisations(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when no outdated organisations are found."""
    requests_mock.get(
        "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        json={
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 0,
            "status_code": 200,
        },
    )

    date = datetime.now().strftime("%Y-%m-%d")
    assert processor(date) is None

    expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_020.value.message.format(
        date=date
    )
    assert expected_log in caplog.text


def test_processor_no_organisations_logs_and_returns(
    mocker: MockerFixture,
) -> None:
    mocker.patch("producer.processor.fetch_outdated_organisations", return_value=[])
    date = datetime.now().strftime("%Y-%m-%d")
    assert processor(date) is None


def test_process_organisation_exception_logs_and_returns_none(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    organisation_resource = {
        "resourceType": "Organization",
        "id": "ANYCODE",
        "name": "Test GP Practice ANYCODE",
        "active": True,
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ANYCODE",
            }
        ],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {"coding": [{"code": "RO177"}]},
                    }
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {"coding": [{"code": "RO76"}]},
                    }
                ],
            },
        ],
    }

    mocker.patch(
        "producer.processor.fetch_organisation_uuid",
        return_value="test-uuid-123",
    )

    mocker.patch(
        "producer.processor.transform_to_payload",
        side_effect=Exception("transform failed"),
    )

    result = processor.__globals__["_process_organisation"](organisation_resource)
    assert result is None
    assert (
        "Error processing organisation with ods_code unknown: transform failed"
        in caplog.text
    )


def test_process_organisation_uuid_not_found(
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test _process_organisation when UUID lookup returns None (empty Bundle)."""
    org_abc123 = {
        "resourceType": "Organization",
        "id": "ABC123",
        "name": "Test GP Practice ABC123",
        "active": True,
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {"coding": [{"code": "RO177"}]},
                    }
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {"coding": [{"code": "RO76"}]},
                    }
                ],
            },
        ],
    }

    # Mock fetch_organisation_uuid to return None (empty Bundle case)
    mocker.patch("producer.processor.fetch_organisation_uuid", return_value=None)

    result = processor.__globals__["_process_organisation"](org_abc123)

    assert result is None
    assert "Organisation UUID not found in internal system" in caplog.text
    assert "ABC123" in caplog.text


def test_process_organisation_not_permitted_skips_transformation(
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    org_not_permitted = {
        "resourceType": "Organization",
        "id": "NOTGP",
        "name": "Not a GP Practice",
        "active": True,
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "NOTGP",
            }
        ],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "code": "RO99",
                                    "display": "Other Service",
                                }
                            ]
                        },
                    }
                ],
            }
        ],
    }

    mock_fetch_uuid = mocker.patch("producer.processor.fetch_organisation_uuid")

    result = processor.__globals__["_process_organisation"](org_not_permitted)

    assert result is None
    mock_fetch_uuid.assert_not_called()
    assert "not a permitted type" in caplog.text.lower()
