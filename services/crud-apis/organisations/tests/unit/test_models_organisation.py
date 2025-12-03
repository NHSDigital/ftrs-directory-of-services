import pytest
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from pydantic import ValidationError

from organisations.app.models.organisation import OrganisationUpdatePayload


def test_valid_payload() -> None:
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
    }
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.active is False
    assert organisation.telecom[0].value == "0123456789"
    assert organisation.type[0].coding[0].code == "GP Service"
    assert organisation.identifier[0].value == "ABC123"


def test_field_too_long_name() -> None:
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "a" * 1000,  # Too long
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "address": [
            {
                "line": ["Example Medical Practice", "Example Street"],
                "city": "Example City",
                "postalCode": "AB12 3CD",
                "country": "ENGLAND",
            }
        ],
    }
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "String should have at most" in str(e.value)


def test_missing_required_field() -> None:
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        # missing identifier which is required
        "name": "Test Organisation",
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "address": [
            {
                "line": ["Example Medical Practice", "Example Street"],
                "city": "Example City",
                "postalCode": "AB12 3CD",
                "country": "ENGLAND",
            }
        ],
    }
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "Field required" in str(e.value)


def test_additional_field() -> None:
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extra_field": "not allowed",
    }
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "Extra inputs are not permitted" in str(e.value)


def test_valid_payload_with_primary_role_code() -> None:
    """Test payload with primary role code extension."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                }
                            ]
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            }
        ],
    }
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.extension is not None
    assert len(organisation.extension) == 1


def test_valid_payload_with_primary_and_non_primary_role_codes() -> None:
    """Test payload with both primary and non-primary role codes."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                }
                            ]
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO76",
                                }
                            ]
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": False},
                ],
            },
        ],
    }
    organisation = OrganisationUpdatePayload(**payload)
    EXPECTED = 2
    assert organisation.name == "Test Organisation"
    assert organisation.extension is not None
    assert len(organisation.extension) == EXPECTED


def test_valid_payload_with_multiple_non_primary_role_codes() -> None:
    """Test payload with multiple non-primary role codes."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                }
                            ]
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO76",
                                }
                            ]
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": False},
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO80",
                                }
                            ]
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": False},
                ],
            },
        ],
    }
    EXPECTED = 3
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.extension is not None
    assert len(organisation.extension) == EXPECTED


def test_valid_payload_with_no_role_codes() -> None:
    """Test payload without any role code extensions."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
    }
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.extension is None


def test_invalid_role_code_not_in_enum() -> None:
    """Test payload with role code that is not a valid OrganisationTypeCode enum value."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "INVALID_CODE",
                                }
                            ]
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            }
        ],
    }

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "Invalid role code: 'INVALID_CODE'" in str(exc_info.value)


def test_missing_role_code_extension() -> None:
    """Test payload with organisation role extension but missing roleCode."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            }
        ],
    }

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "OrganisationRole extension must contain roleCode" in str(exc_info.value)


def test_invalid_extension_url() -> None:
    """Test payload with invalid extension URL."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://invalid.url/Extension",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                }
                            ]
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            }
        ],
    }

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "Invalid extension URL" in str(exc_info.value)


def test_empty_extension_array() -> None:
    """Test payload with organisation role extension but empty nested extension array."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [],
            }
        ],
    }

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "must include a nested 'extension' array" in str(exc_info.value)


def test_role_code_missing_value_codeable_concept() -> None:
    """Test payload with roleCode extension missing valueCodeableConcept."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                    },
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            }
        ],
    }

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "roleCode must have a valueCodeableConcept" in str(exc_info.value)
