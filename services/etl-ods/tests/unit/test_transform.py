from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockFixture

from pipeline.transform import transform_to_payload


def test_transform_to_payload_logs_and_returns_organization(
    mocker: MockFixture,
) -> None:
    ods_fhir = {"resourceType": "Organization", "id": "ODS123", "name": "Test Org"}
    ods_code = "ODS123"
    dos_org_type = "GP Practice"

    fake_organization = mocker.MagicMock()
    fake_organization.identifier = [mocker.MagicMock(value=ods_code)]

    mock_mapper = mocker.patch(
        "pipeline.transform.OrganizationMapper.from_ods_fhir_to_fhir",
        return_value=fake_organization,
    )
    mock_logger = mocker.patch("pipeline.transform.ods_processor_logger.log")

    result = transform_to_payload(ods_fhir, dos_org_type, [])

    mock_mapper.assert_called_once_with(ods_fhir, dos_org_type, [])
    mock_logger.assert_called_once_with(
        OdsETLPipelineLogBase.ETL_PROCESSOR_026,
        ods_code=ods_code,
    )
    assert result == fake_organization
