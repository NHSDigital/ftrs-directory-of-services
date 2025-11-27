import pytest
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from pydantic import ValidationError

from organisations.app.models.organisation import OrganisationUpdatePayload


def _build_base_payload() -> dict:
    return {
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


def test_valid_payload() -> None:
    payload = _build_base_payload()
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.active is False
    assert organisation.telecom[0].value == "0123456789"
    assert organisation.type[0].coding[0].code == "GP Service"
    assert organisation.identifier[0].value == "ABC123"


def test_field_too_long_name() -> None:
    payload = _build_base_payload()
    payload["name"] = "a" * 1000  # Too long
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "String should have at most" in str(e.value)


def test_missing_required_field() -> None:
    payload = _build_base_payload()
    # Remove identifier which is required
    del payload["identifier"]
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "Field required" in str(e.value)


def test_additional_field() -> None:
    payload = _build_base_payload()
    payload["extra"] = "value"
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "Extra inputs are not permitted" in str(e.value)


# Tests for legal date extension validation


def test_valid_typed_period_extension_with_both_dates() -> None:
    """Test valid TypedPeriod extension with both start and end dates."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {
                        "start": "2020-01-15",
                        "end": "2025-12-31",
                    },
                },
            ],
        }
    ]
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is not None
    assert len(organisation.extension) == 1
    ext = organisation.extension[0]
    assert (
        ext.url
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
    )
    # Check sub-extensions
    sub_exts = {e.url: e for e in ext.extension}
    assert "dateType" in sub_exts
    assert "period" in sub_exts
    date_type_ext = sub_exts["dateType"]
    period_ext = sub_exts["period"]
    assert date_type_ext.valueCoding.code == "Legal"
    assert (
        date_type_ext.valueCoding.system
        == "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType"
    )
    assert period_ext.valuePeriod.start == "2020-01-15"
    assert period_ext.valuePeriod.end == "2025-12-31"


def test_valid_typed_period_extension_with_start_only() -> None:
    """Test valid TypedPeriod extension with only start date."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-15"},
                },
            ],
        }
    ]
    organisation = OrganisationUpdatePayload(**payload)
    ext = organisation.extension[0]
    sub_exts = {e.url: e for e in ext.extension}
    period_ext = sub_exts["period"]
    assert period_ext.valuePeriod.start == "2020-01-15"
    assert period_ext.valuePeriod.end is None


def test_valid_typed_period_extension_with_end_only() -> None:
    """Test valid TypedPeriod extension with only end date."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {"end": "2025-12-31"},
                },
            ],
        }
    ]
    organisation = OrganisationUpdatePayload(**payload)
    ext = organisation.extension[0]
    sub_exts = {e.url: e for e in ext.extension}
    period_ext = sub_exts["period"]
    assert period_ext.valuePeriod.start is None
    assert period_ext.valuePeriod.end == "2025-12-31"


def test_invalid_sub_extension() -> None:
    """Test validation fails with invalid sub extension."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert (
        "TypedPeriod extension with URL 'https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod' must include a nested 'extension' array with 'dateType' and 'period' fields"
        in str(e.value)
    )


def test_invalid_extension_url() -> None:
    """Test validation fails with invalid extension URL."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/invalid-extension",
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {"code": "Legal"},
                },
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-15"},
                },
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Invalid extension URL" in str(e.value)


def test_invalid_missing_date_type_sub_extension() -> None:
    """Test validation fails when dateType sub-extension is missing."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "extension": [
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-15"},
                }
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "must contain dateType and period" in str(e.value)


def test_invalid_missing_period_sub_extension() -> None:
    """Test validation fails when period sub-extension is missing."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {"code": "Legal"},
                }
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "must contain dateType and period" in str(e.value)


def test_invalid_non_legal_date_type() -> None:
    """Test validation fails when dateType is not Legal."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Operational",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-15"},
                },
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "dateType must be Legal" in str(e.value)


def test_invalid_period_type_system() -> None:
    """Test validation fails when valueCoding system is not the expected England-PeriodType."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-InvalidPeriodType",
                        "code": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-15"},
                },
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "dateType system must be" in str(e.value)
    assert "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType" in str(e.value)


def test_invalid_period_without_dates() -> None:
    """Test validation fails when period has neither start nor end date."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {},
                },
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "must contain at least start or end date" in str(e.value)


def test_null_extension_is_valid() -> None:
    """Test that null/missing extension field is valid."""
    payload = _build_base_payload()
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is None


def test_invalid_date_format_in_legal_start_date() -> None:
    """Test validation fails when legal start date has invalid format."""
    invalid_dates = [
        "2020-13-45",  # Invalid month and day
        "20-01-2020",  # Wrong format (YY-MM-YYYY)
        "2020/01/15",  # Wrong separator
        "2020-1-5",  # Missing zero padding
        "15-01-2020",  # DD-MM-YYYY instead of YYYY-MM-DD
        "invalid",  # Completely invalid
    ]

    for invalid_date in invalid_dates:
        payload = _build_base_payload()
        payload["extension"] = [
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
                            "start": invalid_date,
                            "end": "2025-12-31",
                        },
                    },
                ],
            }
        ]

        with pytest.raises(ValidationError) as exc_info:
            OrganisationUpdatePayload(**payload)

        assert (
            "datetime" in str(exc_info.value).lower()
            or "date" in str(exc_info.value).lower()
        ), f"Expected validation error for start date: {invalid_date}"


def test_invalid_date_format_in_legal_end_date() -> None:
    """Test validation fails when legal end date has invalid format."""
    invalid_dates = [
        "2025-13-45",  # Invalid month and day
        "25-12-2025",  # Wrong format (YY-MM-YYYY)
        "2025/12/31",  # Wrong separator
        "2025-12-1",  # Missing zero padding
        "31-12-2025",  # DD-MM-YYYY instead of YYYY-MM-DD
    ]

    for invalid_date in invalid_dates:
        payload = _build_base_payload()
        payload["extension"] = [
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
                            "start": "2020-01-15",
                            "end": invalid_date,
                        },
                    },
                ],
            }
        ]

        with pytest.raises(ValidationError) as exc_info:
            OrganisationUpdatePayload(**payload)

        assert (
            "datetime" in str(exc_info.value).lower()
            or "date" in str(exc_info.value).lower()
        ), f"Expected validation error for end date: {invalid_date}"


def test_valid_date_formats_accepted() -> None:
    """Test that properly formatted YYYY-MM-DD dates are accepted."""
    valid_dates = [
        ("2020-01-01", "2025-12-31"),  # Standard dates
        ("2020-02-29", "2024-02-29"),  # Leap year dates
        ("2020-01-15", "2025-12-31"),  # Original test dates
    ]

    for start_date, end_date in valid_dates:
        payload = _build_base_payload()
        payload["extension"] = [
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
                            "start": start_date,
                            "end": end_date,
                        },
                    },
                ],
            }
        ]

        organisation = OrganisationUpdatePayload(**payload)
        assert organisation.extension is not None, (
            f"Valid dates {start_date} to {end_date} should be accepted"
        )


def test_invalid_legal_period_start_equals_end() -> None:
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": "Legal",
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {
                        "start": "2022-01-01",
                        "end": "2022-01-01",
                    },
                },
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Legal period start and end dates must not be equal" in str(e.value)


def test_valid_organisation_role_extension_with_typed_period() -> None:
    """Test valid OrganisationRole extension containing a TypedPeriod extension."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {"url": "instanceID", "valueInteger": 12345},
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
                            "valuePeriod": {"start": "2020-01-15", "end": "2025-12-31"},
                        },
                    ],
                },
            ],
        }
    ]
    organisation = OrganisationUpdatePayload(**payload)
    assert len(organisation.extension) == 1

    role_ext = organisation.extension[0]
    assert (
        role_ext.url
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
    )

    # Find the TypedPeriod extension within the role extension
    typed_period_ext = next(
        (
            ext
            for ext in role_ext.extension
            if ext.url
            == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        ),
        None,
    )
    assert typed_period_ext is not None

    sub_exts = {e.url: e for e in typed_period_ext.extension}
    assert "dateType" in sub_exts
    assert "period" in sub_exts
    assert sub_exts["dateType"].valueCoding.code == "Legal"
    assert sub_exts["period"].valuePeriod.start == "2020-01-15"
    assert sub_exts["period"].valuePeriod.end == "2025-12-31"


def test_valid_organisation_role_extension_with_multiple_typed_periods() -> None:
    """Test valid OrganisationRole extension containing multiple TypedPeriod extensions - only first is validated."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {"url": "instanceID", "valueInteger": 12345},
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
                            "valuePeriod": {"start": "2020-01-15", "end": "2022-12-31"},
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
                                "code": "NotLegal",  # This would fail validation if checked, but it's the second one
                                "display": "Not Legal",
                            },
                        },
                        {
                            "url": "period",
                            "valuePeriod": {"start": "2023-01-01", "end": "2025-12-31"},
                        },
                    ],
                },
            ],
        }
    ]
    # Should pass because only the first TypedPeriod extension is validated
    organisation = OrganisationUpdatePayload(**payload)
    role_ext = organisation.extension[0]

    # Find the first TypedPeriod extension within the role extension
    first_typed_period_ext = next(
        (
            ext
            for ext in role_ext.extension
            if ext.url
            == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        ),
        None,
    )
    assert first_typed_period_ext is not None

    # Validate the first TypedPeriod extension structure
    sub_exts = {e.url: e for e in first_typed_period_ext.extension}
    assert "dateType" in sub_exts
    assert "period" in sub_exts
    assert sub_exts["dateType"].valueCoding.code == "Legal"  # First one should be Legal
    assert sub_exts["period"].valuePeriod.start == "2020-01-15"


def test_invalid_first_typed_period_fails_validation() -> None:
    """Test that invalid first TypedPeriod extension fails validation even if later ones are valid."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {"url": "instanceID", "valueInteger": 12345},
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {
                                "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                "code": "NotLegal",  # This is invalid and is the first one
                                "display": "Not Legal",
                            },
                        },
                        {
                            "url": "period",
                            "valuePeriod": {"start": "2020-01-15"},
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
                                "code": "Legal",  # This is valid but is the second one
                                "display": "Legal",
                            },
                        },
                        {
                            "url": "period",
                            "valuePeriod": {"start": "2023-01-01"},
                        },
                    ],
                },
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "dateType must be Legal" in str(e.value)


def test_invalid_organisation_role_extension_empty_extension_array() -> None:
    """Test OrganisationRole extension with empty extension array fails validation."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "OrganisationRole extension" in str(e.value)
    assert "must include a nested 'extension' array" in str(e.value)


def test_invalid_organisation_role_extension_missing_extension_array() -> None:
    """Test OrganisationRole extension without extension array fails validation."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
            # Missing extension array
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "OrganisationRole extension" in str(e.value)
    assert "must include a nested 'extension' array" in str(e.value)


def test_invalid_typed_period_in_organisation_role_missing_date_type() -> None:
    """Test TypedPeriod extension within OrganisationRole with missing dateType fails."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "period",
                            "valuePeriod": {"start": "2020-01-15"},
                        },
                    ],
                }
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "TypedPeriod extension must contain dateType and period" in str(e.value)


def test_invalid_typed_period_in_organisation_role_invalid_date_type() -> None:
    """Test TypedPeriod extension within OrganisationRole with invalid dateType fails."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {
                                "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                "code": "NotLegal",
                                "display": "Not Legal",
                            },
                        },
                        {
                            "url": "period",
                            "valuePeriod": {"start": "2020-01-15"},
                        },
                    ],
                }
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "dateType must be Legal" in str(e.value)


def test_invalid_typed_period_in_organisation_role_invalid_system() -> None:
    """Test TypedPeriod extension within OrganisationRole with invalid system fails."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {
                                "system": "https://invalid.system.url",
                                "code": "Legal",
                                "display": "Legal",
                            },
                        },
                        {
                            "url": "period",
                            "valuePeriod": {"start": "2020-01-15"},
                        },
                    ],
                }
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert (
        "dateType system must be 'https://fhir.nhs.uk/England/CodeSystem/England-PeriodType'"
        in str(e.value)
    )


def test_invalid_typed_period_in_organisation_role_no_period_dates() -> None:
    """Test TypedPeriod extension within OrganisationRole with no period dates fails."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
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
                            "valuePeriod": {},
                        },
                    ],
                }
            ],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "period must contain at least start or end date" in str(e.value)


def test_no_role_extension() -> None:
    """Test unknown extension URL fails validation."""
    payload = _build_base_payload()
    payload["extension"] = [{"url": "https://invalid.extension.url", "extension": []}]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Invalid extension URL: https://invalid.extension.url" in str(e.value)


def test_organisation_role_with_no_typed_periods_is_valid() -> None:
    """Test OrganisationRole extension without TypedPeriod extensions is valid."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {"url": "instanceID", "valueInteger": 12345},
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
            ],
        }
    ]
    organisation = OrganisationUpdatePayload(**payload)
    assert len(organisation.extension) == 1
    role_ext = organisation.extension[0]
    assert (
        role_ext.url
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
    )
