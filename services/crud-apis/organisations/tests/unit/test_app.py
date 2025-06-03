from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from botocore.exceptions import ClientError
from fastapi import HTTPException
from ftrs_data_layer.models import Endpoint, Organisation
from ftrs_data_layer.repository.dynamodb.document_level import DocumentLevelRepository

from organisations.app import (
    apply_updates,
    get_org_id,
    get_outdated_fields,
    get_repository,
    get_table_name,
    read_many_organisations,
    read_organisation,
    update_organisation,
)
from organisations.settings import AppSettings
from organisations.validators import UpdatePayloadValidator


def make_organisation(**overrides: object) -> Organisation:
    defaults = dict(
        id=uuid4(),
        identifier_ODS_ODSCode="123456",
        active=True,
        name="Test Organisation",
        telecom="123456789",
        type="NHS",
        createdBy="user",
        createdDateTime=datetime(2023, 10, 1, tzinfo=timezone.utc),
        modifiedBy="user",
        modifiedDateTime=datetime(2023, 10, 1, tzinfo=timezone.utc),
        endpoints=[],
    )
    defaults.update(overrides)
    return Organisation(**defaults)


@pytest.mark.parametrize(
    "existing_data, payload_data, expected_outdated_fields",
    [
        (
            {
                "id": "00000000-0000-0000-0000-00000000000a",
                "identifier_ODS_ODSCode": "123456",
                "active": True,
                "name": "Test Organisation",
                "telecom": "123456789",
                "type": "NHS",
                "createdBy": "test_user",
                "createdDateTime": "2023-10-01T00:00:00Z",
                "modifiedBy": "test_user",
                "modifiedDateTime": "2023-10-01T00:00:00Z",
            },
            {
                "name": "New Name",
                "telecom": "123456789",
                "active": True,
                "type": "GP Practice",
                "modified_by": "other_user",
            },
            {"name": "New Name", "type": "GP Practice", "modified_by": "other_user"},
        ),
        (
            {
                "id": "00000000-0000-0000-0000-00000000000a",
                "identifier_ODS_ODSCode": "123456",
                "active": True,
                "name": "Test Organisation",
                "telecom": "123456789",
                "type": "NHS",
                "createdBy": "test_user",
                "createdDateTime": "2023-10-01T00:00:00Z",
                "modifiedBy": "test_user",
                "modifiedDateTime": "2023-10-01T00:00:00Z",
            },
            {
                "name": "Test Organisation",
                "telecom": "123456789",
                "active": True,
                "type": "NHS",
                "modified_by": "test_user",
            },
            {},
        ),
    ],
)
def test_get_outdated_fields(
    existing_data: dict[str, str],
    payload_data: dict[str, str],
    expected_outdated_fields: dict[str, str],
) -> None:
    organisation = make_organisation(**existing_data)
    payload = UpdatePayloadValidator(**payload_data)
    outdated_fields = get_outdated_fields(organisation, payload)
    assert outdated_fields == expected_outdated_fields


def test_apply_updates() -> None:
    organisation = make_organisation()
    outdated_fields = {"name": "New Name", "modified_by": "new_user"}
    apply_updates(organisation, outdated_fields)
    assert organisation.name == "New Name"
    assert organisation.modifiedBy == "new_user"
    assert organisation.modifiedDateTime != datetime(2023, 10, 1, tzinfo=timezone.utc)


@patch("organisations.app.get_repository")
def test_update_organisation_no_changes(
    mock_get_repository: MagicMock,
) -> None:
    mock_repo = MagicMock()
    organisation_id = uuid4()
    mock_repo.get.return_value = make_organisation(id=organisation_id)
    mock_get_repository.return_value = mock_repo

    payload = UpdatePayloadValidator(
        name="Test Organisation",
        active=True,
        telecom="123456789",
        modified_by="user",
        type="NHS",
    )
    response = update_organisation(
        organisation_id, payload, AppSettings(ENVIRONMENT="test")
    )

    # Assert the response
    assert str(response.status_code) == "200"
    assert response.body.decode("utf-8") == '{"message":"No changes detected"}'


def test_apply_updates_converts_id_str_to_uuid() -> None:
    org = make_organisation()
    org.id = "56b7e12f-beb2-4d4d-a9e0-09eaa195838d"
    apply_updates(org, {})
    assert isinstance(org.id, UUID)


def test_apply_updates_converts_createdDateTime_str_to_datetime() -> None:
    org = make_organisation()
    org.createdDateTime = "2025-05-02T14:01:14.600040Z"
    apply_updates(org, {})
    assert isinstance(org.id, UUID)


def test_apply_updates_convert_dict_endpoint_to_model() -> None:
    endpoint_dicts = [
        {
            "id": "d5a852ef-12c7-4014-b398-661716a63027",
            "address": "https://example.com/endpoint",
            "connectionType": "itk",
            "description": "Primary",
            "payloadMimeType": "xml",
            "identifier_oldDoS_id": 67890,
            "isCompressionEnabled": True,
            "managedByOrganisation": "d5a852ef-12c7-4014-b398-661716a63027",
            "createdBy": "ROBOT",
            "createdDateTime": "2023-10-01T00:00:00Z",
            "modifiedBy": "ROBOT",
            "modifiedDateTime": "2023-10-01T00:00:00Z",
            "name": None,
            "order": 1,
            "payloadType": "urn:nhs:example:interaction",
            "service": None,
            "status": "active",
        },
    ]
    org = make_organisation()
    org.endpoints = endpoint_dicts
    apply_updates(org, {})
    assert all(isinstance(e, Endpoint) for e in org.endpoints)


def test_apply_updates_endpoints_empty_list() -> None:
    org = make_organisation(endpoints=[])
    apply_updates(org, {})
    assert org.endpoints == []


def test_apply_updates_endpoints_list_of_models() -> None:
    endpoint_models = [
        Endpoint(
            id=uuid4(),
            identifier_oldDoS_id=123456,
            status="active",
            connectionType="itk",
            description="Test Endpoint",
            payloadMimeType="xml",
            identifier_oldDoS_uid="123456",
            isCompressionEnabled=True,
            managedByOrganisation=uuid4(),
            createdBy="test_user",
            createdDateTime="2023-10-01T00:00:00Z",
            modifiedBy="test_user",
            modifiedDateTime="2023-10-01T00:00:00Z",
            name="Test Endpoint Name",
            payloadType="urn:nhs:example:interaction",
            service=None,
            address="https://example.com/endpoint",
            order=1,
        ),
    ]
    org = make_organisation(endpoints=endpoint_models)
    apply_updates(org, {})
    assert all(isinstance(e, Endpoint) for e in org.endpoints)


@patch("organisations.app.get_repository")
def test_update_organisation_with_changes(
    mock_get_repository: MagicMock,
) -> None:
    mock_repo = MagicMock()
    organisation_id = uuid4()
    mock_repo.get.return_value = make_organisation(id=organisation_id)
    mock_get_repository.return_value = mock_repo

    payload = UpdatePayloadValidator(
        name="New Name",
        active=True,
        telecom="123456789",
        modified_by="test_user",
        type="NHS",
    )

    response = update_organisation(
        organisation_id, payload, AppSettings(ENVIRONMENT="test")
    )

    mock_repo.get.assert_called_once_with(organisation_id)
    mock_repo.update.assert_called_once()
    assert str(response.status_code) == "200"
    assert response.body.decode("utf-8") == '{"message":"Data processed successfully"}'


@patch("organisations.app.get_repository")
def test_update_organisation_not_found(
    mock_get_repository: MagicMock,
) -> None:
    mock_repo = MagicMock()
    mock_repo.get.return_value = None
    mock_get_repository.return_value = mock_repo

    payload = UpdatePayloadValidator(
        name="NHS Digital",
        active=True,
        telecom="123456789",
        modified_by="test_user",
        type="NHS",
    )
    with pytest.raises(HTTPException) as e:
        update_organisation(uuid4(), payload, AppSettings(ENVIRONMENT="test"))

    assert str(e.value.status_code) == "404"
    assert str(e.value.detail) == "Organisation not found"


@patch("organisations.app.get_repository")
def test_update_organisation_internal_server_error(
    mock_get_repository: MagicMock,
) -> None:
    payload = UpdatePayloadValidator(
        name="NHS Digital",
        active=True,
        telecom="123456789",
        modified_by="test_user",
        type="NHS",
    )

    error_response = {
        "Error": {
            "Code": "InternalServerError",
            "Message": "An internal server error occurred.",
        }
    }
    mock_get_repository.side_effect = ClientError(error_response, "PutItem")

    with pytest.raises(Exception) as e:
        update_organisation("X26", payload, AppSettings(ENVIRONMENT="test"))

    assert e.value.response["Error"]["Code"] == "InternalServerError"
    assert e.value.response["Error"]["Message"] == "An internal server error occurred."


@patch("organisations.app.get_repository")
def test_get_org_by_ods_code_success(mock_get_repository: MagicMock) -> None:
    mock_repository = MagicMock()
    mock_repository.get_by_ods_code.return_value = ["uuid"]
    mock_get_repository.return_value = mock_repository

    response = get_org_id("ods_code", AppSettings(ENVIRONMENT="test"))

    mock_repository.get_by_ods_code.assert_called_once_with("ods_code")

    assert str(response.status_code) == "200"
    assert response.body.decode("utf-8") == '{"id":"uuid"}'


@patch("organisations.app.get_repository")
def test_get_org_id_not_found(mock_get_repository: MagicMock) -> None:
    mock_repository = MagicMock()
    mock_get_repository.return_value = mock_repository
    mock_repository.get_by_ods_code.return_value = None

    with pytest.raises(HTTPException) as e:
        get_org_id("uuid", AppSettings(ENVIRONMENT="test"))

    assert str(e.value.status_code) == "404"
    assert str(e.value.detail) == "Organisation not found"


@patch("organisations.app.get_repository")
def test_read_organisation_by_id_returns_organisation_if_exists(
    mock_get_repository: MagicMock,
) -> None:
    mock_repo = MagicMock()
    mock_repo.get.return_value = {
        "id": "00000000-0000-0000-0000-11111111111",
        "name": "Test Organisation",
    }
    mock_get_repository.return_value = mock_repo
    response = read_organisation(
        "/00000000-0000-0000-0000-11111111111", AppSettings(ENVIRONMENT="test")
    )

    assert response == {
        "id": "00000000-0000-0000-0000-11111111111",
        "name": "Test Organisation",
    }


@patch("organisations.app.get_repository")
def test_read_organisation_not_found(
    mock_get_repository: MagicMock,
) -> None:
    mock_repo = MagicMock()
    mock_repo.get.return_value = None
    mock_get_repository.return_value = mock_repo

    with pytest.raises(HTTPException) as e:
        read_organisation("notARealID", AppSettings(ENVIRONMENT="test"))

    assert str(e.value.status_code) == "404"
    assert str(e.value.detail) == "Organisation not found"


@patch("organisations.app.get_repository")
def test_read_many_organisations_success(
    mock_get_repository: MagicMock,
) -> None:
    mock_repo = MagicMock()
    org_id = uuid4()
    mock_repo.iter_records.return_value = [
        Organisation(
            id=org_id,
            identifier_ODS_ODSCode="123456",
            active=True,
            name="Test Organisation",
            telecom="123456789",
            type="NHS",
            createdBy="test_user",
            createdDateTime="2023-10-01T00:00:00Z",
            modifiedBy="test_user",
            modifiedDateTime="2023-10-01T00:00:00Z",
        )
    ]
    mock_get_repository.return_value = mock_repo

    response = read_many_organisations(AppSettings(ENVIRONMENT="test"))

    assert response == [
        Organisation(
            id=org_id,
            identifier_ODS_ODSCode="123456",
            active=True,
            name="Test Organisation",
            telecom="123456789",
            type="NHS",
            createdBy="test_user",
            createdDateTime="2023-10-01T00:00:00Z",
            modifiedBy="test_user",
            modifiedDateTime="2023-10-01T00:00:00Z",
        )
    ]


@patch("organisations.app.get_repository")
def test_read_many_organisations_not_found(
    mock_get_repository: MagicMock,
) -> None:
    mock_repo = MagicMock()
    mock_repo.iter_records.return_value = []
    mock_get_repository.return_value = mock_repo

    with pytest.raises(HTTPException) as e:
        read_many_organisations(AppSettings(ENVIRONMENT="test"))

    assert str(e.value.status_code) == "404"
    assert str(e.value.detail) == "Unable to retrieve any organisations"


def test_get_repository() -> None:
    repository = get_repository()
    assert isinstance(repository, DocumentLevelRepository)


@pytest.mark.parametrize(
    "entity_type, env, workspace, expected_table_name",
    [
        ("organisation", "local", None, "ftrs-dos-local-database-organisation"),
        ("organisation", "dev", "test", "ftrs-dos-dev-database-organisation-test"),
        ("service", "prod", None, "ftrs-dos-prod-database-service"),
        ("service", "qa", "workspace1", "ftrs-dos-qa-database-service-workspace1"),
    ],
)
def test_get_table_name(
    entity_type: str, env: str, workspace: str | None, expected_table_name: str
) -> None:
    """
    Test get_table_name function with various inputs.
    """
    result = get_table_name(entity_type, env, workspace)
    assert result == expected_table_name
