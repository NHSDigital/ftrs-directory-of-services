from src.models.constants import (
    FHIR_HTTP_ERROR_CODES_SYSTEM,
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    OPERATION_OUTCOME_SYSTEM,
)

# GET /Organization - 200 Success Bundle
SUCCESS_BUNDLE_ABC123 = {
    "resourceType": "Bundle",
    "type": "searchset",
    "total": 1,
    "entry": [
        {
            "fullUrl": "https://api.service.nhs.uk/FHIR/R4/Organization/04393ec4-198f-42dd-9507-f4fa5e9ebf96",
            "resource": {
                "resourceType": "Organization",
                "id": "04393ec4-198f-42dd-9507-f4fa5e9ebf96",
                "identifier": [
                    {
                        "system": ODS_ORG_CODE_IDENTIFIER_SYSTEM,
                        "value": "ABC123",
                    }
                ],
                "extension": [
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
                                            "start": "2020-01-15",
                                            "end": "2025-12-31",
                                        },
                                    },
                                ],
                            },
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
                                            "display": "GP PRACTICE",
                                        }
                                    ]
                                },
                            }
                        ],
                    },
                ],
                "active": True,
                "name": "Example Organization",
                "telecom": [
                    {"system": "phone", "value": "01234 567890"},
                    {"system": "email", "value": "example@example.com"},
                ],
                "address": [
                    {
                        "line": ["Example Medical Practice", "Example Street"],
                        "city": "Example City",
                        "postalCode": "AB12 3CD",
                        "country": "ENGLAND",
                    }
                ],
            },
        }
    ],
}

# GET /Organization - 404 Not Found
ERROR_NOT_FOUND = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "not-found",
            "details": {
                "coding": [
                    {
                        "system": OPERATION_OUTCOME_SYSTEM,
                        "code": "MSG_NO_EXIST",
                        "display": "Resource does not exist",
                    }
                ],
                "text": "The requested organisation was not found",
            },
            "diagnostics": "Organisation with ODS code 'DEF456' not found",
        }
    ],
}

# GET /Organization - 400 Missing identifier parameter
ERROR_MISSING_IDENTIFIER = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "required",
            "details": {
                "coding": [
                    {
                        "system": FHIR_HTTP_ERROR_CODES_SYSTEM,
                        "code": "BAD_REQUEST",
                        "display": "The Server was unable to process the request.",
                    }
                ],
                "text": "Missing required parameter: identifier",
            },
            "diagnostics": "The 'identifier' query parameter is required",
        }
    ],
}

# GET /Organization - 400 Missing identifier separator
ERROR_MISSING_IDENTIFIER_SEPARATOR = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "structure",
            "details": {
                "coding": [
                    {
                        "system": FHIR_HTTP_ERROR_CODES_SYSTEM,
                        "code": "BAD_REQUEST",
                        "display": "The Server was unable to process the request.",
                    }
                ],
                "text": "Invalid identifier value: missing separator '|'. Must be in format 'https://fhir.nhs.uk/Id/ods-organization-code|<code>' and code must follow format ^[A-Za-z0-9]{1,12}$",
            },
            "diagnostics": "Invalid identifier value: missing separator '|'. Must be in format 'https://fhir.nhs.uk/Id/ods-organization-code|<code>' and code must follow format ^[A-Za-z0-9]{1,12}$",
        }
    ],
}

# GET /Organization - 400 Invalid identifier system
ERROR_INVALID_IDENTIFIER_SYSTEM = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "structure",
            "details": {
                "coding": [
                    {
                        "system": FHIR_HTTP_ERROR_CODES_SYSTEM,
                        "code": "BAD_REQUEST",
                        "display": "The Server was unable to process the request.",
                    }
                ],
                "text": f"Invalid identifier system - expected '{ODS_ORG_CODE_IDENTIFIER_SYSTEM}'",
            },
            "diagnostics": f"Invalid identifier system - expected '{ODS_ORG_CODE_IDENTIFIER_SYSTEM}'",
        }
    ],
}

# GET /Organization - 400 Invalid ODS code format
ERROR_INVALID_IDENTIFIER_VALUE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "invalid",
            "details": {
                "coding": [
                    {
                        "system": FHIR_HTTP_ERROR_CODES_SYSTEM,
                        "code": "BAD_REQUEST",
                        "display": "The Server was unable to process the request.",
                    }
                ],
                "text": "Invalid identifier value: ODS code must follow format ^[A-Za-z0-9]{1,12}$",
            },
            "diagnostics": "Invalid identifier value: ODS code must follow format ^[A-Za-z0-9]{1,12}$",
        }
    ],
}

# GET /Organization - 500 Internal Server Error
ERROR_INTERNAL_SERVER = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "fatal",
            "code": "exception",
            "details": {
                "coding": [
                    {
                        "system": FHIR_HTTP_ERROR_CODES_SYSTEM,
                        "code": "SERVER_ERROR",
                        "display": "The Server has encountered an error processing the request.",
                    }
                ],
                "text": "Unhandled exception occurred",
            },
            "diagnostics": "Unhandled exception occurred",
        }
    ],
}

# PUT /Organization/{id} - 200 Success
PUT_SUCCESS_RESPONSE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "information",
            "code": "informational",
            "details": {
                "coding": [
                    {
                        "system": OPERATION_OUTCOME_SYSTEM,
                        "code": "MSG_UPDATED",
                        "display": "Existing resource updated",
                    }
                ],
                "text": "Organisation updated successfully",
            },
            "diagnostics": "Organisation updated successfully",
        }
    ],
}

# PUT /Organization/{id} - 404 Not Found
PUT_NOT_FOUND_RESPONSE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "not-found",
            "details": {
                "coding": [
                    {
                        "system": FHIR_HTTP_ERROR_CODES_SYSTEM,
                        "code": "NOT_FOUND",
                        "display": "The Server was unable to find the specified resource.",
                    }
                ],
                "text": "The requested organisation was not found",
            },
            "diagnostics": "Organisation not found.",
        }
    ],
}
