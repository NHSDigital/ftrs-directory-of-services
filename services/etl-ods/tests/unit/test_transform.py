from pytest_mock import MockFixture

from transformer.transform import transform_to_payload


def test_transform_to_payload_returns_organization(
    mocker: MockFixture,
) -> None:
    ods_fhir = {"resourceType": "Organization", "id": "ODS123", "name": "Test Org"}

    fake_organization = mocker.MagicMock()
    fake_organization.identifier = [mocker.MagicMock(value="ODS123")]

    mock_mapper = mocker.patch(
        "transformer.transform.OrganizationMapper.from_ods_fhir_to_fhir",
        return_value=fake_organization,
    )

    result = transform_to_payload(ods_fhir)

    mock_mapper.assert_called_once_with(ods_fhir)
    assert result == fake_organization
