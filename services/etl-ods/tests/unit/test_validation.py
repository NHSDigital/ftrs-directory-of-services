# """Unit tests for validation.py module."""

# import pytest
# from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
# from ftrs_data_layer.domain.enums import OrganisationType
# from pytest_mock import MockFixture

# from pipeline.validation import (
#     GP_PRACTICE_ROLE_CODE,
#     PRESCRIBING_COST_CENTRE_CODE,
#     get_permitted_org_type,
# )


# def test_is_gp_valid_gp_practice(
#     caplog: pytest.LogCaptureFixture,
# ) -> None:
#     """Test organization with RO177 and RO76."""
#     ods_org = {
#         "identifier": [
#             {
#                 "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#                 "value": "GP001",
#             }
#         ],
#         "extension": [
#             {
#                 "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
#                 "extension": [
#                     {
#                         "url": "roleCode",
#                         "valueCodeableConcept": {"coding": [{"code": "RO177"}]},
#                     }
#                 ],
#             },
#             {
#                 "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
#                 "extension": [
#                     {
#                         "url": "roleCode",
#                         "valueCodeableConcept": {"coding": [{"code": "RO76"}]},
#                     }
#                 ],
#             },
#         ],
#     }
#     _mapper = OrganizationMapper()
#     result = is_gp(ods_org, _mapper)
#     assert result is True
#     assert "Type maps to GP Practice." in caplog.text


# def test_is_gp_invalid_missing_roles() -> None:
#     """Test organization with RO177 but without gp role"""
#     ods_org = {
#         "identifier": [
#             {
#                 "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#                 "value": "NOTGP001",
#             }
#         ],
#     }
#     _mapper = OrganizationMapper()
#     result = is_gp(ods_org, _mapper)
#     assert result is False


# def test_is_gp_invalid_missing_cost_centre_role(
#     caplog: pytest.LogCaptureFixture,
# ) -> None:
#     """Test organization with RO177 but without cost centre role"""
#     ods_org = {
#         "identifier": [
#             {
#                 "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#                 "value": "NOTGP001",
#             }
#         ],
#         "extension": [
#             {
#                 "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
#                 "extension": [
#                     {
#                         "url": "roleCode",
#                         "valueCodeableConcept": {"coding": [{"code": "RO76"}]},
#                     }
#                 ],
#             },
#         ],
#     }
#     _mapper = OrganizationMapper()
#     result = is_gp(ods_org, _mapper)
#     assert result is False
#     assert f"Role {PRESCRIBING_COST_CENTRE_CODE} not found" in caplog.text


# def test_is_gp_invalid_missing_gp_role(
#     caplog: pytest.LogCaptureFixture,
# ) -> None:
#     """Test organization with RO177 but without gp role"""
#     ods_org = {
#         "identifier": [
#             {
#                 "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#                 "value": "NOTGP001",
#             }
#         ],
#         "extension": [
#             {
#                 "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
#                 "extension": [
#                     {
#                         "url": "roleCode",
#                         "valueCodeableConcept": {"coding": [{"code": "RO177"}]},
#                     }
#                 ],
#             },
#         ],
#     }
#     _mapper = OrganizationMapper()
#     result = is_gp(ods_org, _mapper)
#     assert result is False
#     assert "No GP Practice mapped roles found." in caplog.text


# def test_valid_with_multiple_gp_roles() -> None:
#     """Test organization with multiple valid GP roles."""
#     ods_org = {
#         "identifier": [
#             {
#                 "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#                 "value": "GP004",
#             }
#         ],
#         "extension": [
#             {
#                 "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
#                 "extension": [
#                     {
#                         "url": "roleCode",
#                         "valueCodeableConcept": {"coding": [{"code": "RO177"}]},
#                     }
#                 ],
#             },
#             {
#                 "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
#                 "extension": [
#                     {
#                         "url": "roleCode",
#                         "valueCodeableConcept": {"coding": [{"code": "RO76"}]},
#                     }
#                 ],
#             },
#             {
#                 "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
#                 "extension": [
#                     {
#                         "url": "roleCode",
#                         "valueCodeableConcept": {"coding": [{"code": "ABC"}]},
#                     }
#                 ],
#             },
#         ],
#     }
#     _mapper = OrganizationMapper()
#     result = is_gp(ods_org, _mapper)
#     assert result is True


# def test_returns_gp_practice_for_valid_org(
#     mocker: MockFixture, caplog: pytest.LogCaptureFixture
# ) -> None:
#     """Test returns GP_PRACTICE for valid organization."""
#     ods_org = {
#         "identifier": [
#             {
#                 "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#                 "value": "GP001",
#             }
#         ],
#     }

#     mock_is_gp = mocker.patch(
#         "pipeline.validation.is_gp",
#         return_value=True,
#     )

#     result = get_permitted_org_type(ods_org)
#     assert result == OrganisationType.GP_PRACTICE
#     mock_is_gp.assert_called_once()
#     assert "Checking if organisation is permitted type" in caplog.text


# def test_returns_none_for_invalid_org(mocker: MockFixture) -> None:
#     """Test returns None for non-permitted organization."""
#     ods_org = {
#         "identifier": [
#             {
#                 "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#                 "value": "NOTGP001",
#             }
#         ],
#     }

#     mock_is_gp = mocker.patch(
#         "pipeline.validation.is_gp",
#         return_value=False,
#     )

#     result = get_permitted_org_type(ods_org)
#     assert result is None
#     mock_is_gp.assert_called_once()


# def test_prescribing_cost_centre_code() -> None:
#     """Test PRESCRIBING_COST_CENTRE_CODE constant."""
#     assert PRESCRIBING_COST_CENTRE_CODE == "RO177"


# def test_gp_practice_role_code() -> None:
#     """Test GP_PRACTICE_ROLE_CODE constant."""
#     assert GP_PRACTICE_ROLE_CODE == "RO76"
