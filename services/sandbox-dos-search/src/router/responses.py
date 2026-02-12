# Stubbed responses for the dos-search sandbox, aligned with docs/specification/dos-search.yaml

from src.models.constants import (
    INVALID_SEARCH_DATA_DISPLAY,
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
    SPINE_ERROR_OR_WARNING_CODE_SYSTEM,
)

SUCCESS_BUNDLE_ABC123 = {
    "resourceType": "Bundle",
    "id": "87c5f637-cca3-4ddd-97a9-a3f6e6746bbe",
    "type": "searchset",
    "link": [
        {
            "relation": "self",
            # Reflect FHIR search parameter and required reverse include
            "url": f"https://api.service.nhs.uk/FHIR/R4/Organization?identifier={ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123&_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}",
        }
    ],
    "entry": [
        {
            "fullUrl": "https://api.service.nhs.uk/FHIR/R4/Organization/04393ec4-198f-42dd-9507-f4fa5e9ebf96",
            "resource": {
                "resourceType": "Organization",
                "id": "04393ec4-198f-42dd-9507-f4fa5e9ebf96",
                "identifier": [
                    {
                        "use": "official",
                        "system": ODS_ORG_CODE_IDENTIFIER_SYSTEM,
                        "value": "ABC123",
                    }
                ],
                "active": True,
                "name": "Example Organization",
            },
            "search": {"mode": "match"},
        },
        {
            "fullUrl": "https://api.service.nhs.uk/FHIR/R4/Endpoint/1b62110d-4db5-4230-bf37-cbe948aecf76",
            "resource": {
                "resourceType": "Endpoint",
                "id": "1b62110d-4db5-4230-bf37-cbe948aecf76",
                "extension": [
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganizationEndpointOrder",
                        "valueInteger": 1,
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointCompression",
                        "valueBoolean": False,
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointBusinessScenario",
                        "valueCode": "primary-recipient",
                    },
                ],
                "status": "active",
                "connectionType": {
                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-EndpointConnection",
                    "code": "email",
                },
                "managingOrganization": {
                    "reference": "Organization/04393ec4-198f-42dd-9507-f4fa5e9ebf96"
                },
                "payloadType": [
                    {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                                "code": "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0",
                            }
                        ]
                    }
                ],
                "payloadMimeType": ["application/pdf"],
                "address": "dummy-endpoint-email@nhs.net",
            },
            "search": {"mode": "include"},
        },
        {
            "fullUrl": "https://api.service.nhs.uk/FHIR/R4/Endpoint/5df57f63-7f48-5754-b056-ba362834c1e7",
            "resource": {
                "resourceType": "Endpoint",
                "id": "5df57f63-7f48-5754-b056-ba362834c1e7",
                "extension": [
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganizationEndpointOrder",
                        "valueInteger": 2,
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointCompression",
                        "valueBoolean": False,
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointBusinessScenario",
                        "valueCode": "copy-recipient",
                    },
                ],
                "status": "active",
                "connectionType": {
                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-EndpointConnection",
                    "code": "email",
                },
                "managingOrganization": {
                    "reference": "Organization/04393ec4-198f-42dd-9507-f4fa5e9ebf96"
                },
                "payloadType": [
                    {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                                "code": "urn:nhs-itk:interaction:copyRecipientNHS111CDADocument-v2-0",
                            }
                        ]
                    }
                ],
                "payloadMimeType": ["application/pdf"],
                "address": "dummy-endpoint-email@nhs.net",
            },
            "search": {"mode": "include"},
        },
    ],
}

ERROR_INVALID_IDENTIFIER_VALUE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "value",
            "details": {
                "coding": [
                    {
                        "system": SPINE_ERROR_OR_WARNING_CODE_SYSTEM,
                        "version": "1.0.0",
                        "code": "INVALID_SEARCH_DATA",
                        "display": INVALID_SEARCH_DATA_DISPLAY,
                    }
                ]
            },
            "diagnostics": "Invalid identifier value: ODS code 'ABC' must follow format ^[A-Za-z0-9]{5,12}$",
        }
    ],
}

ERROR_MISSING_REVINCLUDE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "value",
            "details": {
                "coding": [
                    {
                        "system": SPINE_ERROR_OR_WARNING_CODE_SYSTEM,
                        "version": "1.0.0",
                        "code": "INVALID_SEARCH_DATA",
                        "display": INVALID_SEARCH_DATA_DISPLAY,
                    }
                ]
            },
            "diagnostics": f"The request is missing the '_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}' parameter, which is required to include linked Endpoint resources.",
        }
    ],
}

ERROR_INVALID_IDENTIFIER_SYSTEM = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "code-invalid",
            "details": {
                "coding": [
                    {
                        "system": SPINE_ERROR_OR_WARNING_CODE_SYSTEM,
                        "version": "1.0.0",
                        "code": "INVALID_SEARCH_DATA",
                        "display": INVALID_SEARCH_DATA_DISPLAY,
                    }
                ]
            },
            "diagnostics": f"Invalid identifier system 'foo' - expected '{ODS_ORG_CODE_IDENTIFIER_SYSTEM}'",
        }
    ],
}
