GET_SUCCESS_RESPONSE = {
    "resourceType": "Bundle",
    "id": "87c5f637-cca3-4ddd-97a9-a3f6e6746bbe",
    "type": "searchset",
    "link": [
        {
            "relation": "self",
            "url": "https://api.service.nhs.uk/FHIR/R4/Organization?identifier=odsOrganisationCode|ABC123"
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
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "ABC123"
                    }
                ],
                "active": True,
                "name": "Example Organization",
                "telecom": [
                    {
                        "system": "phone",
                        "value": "01234 567890"
                    },
                    {
                        "system": "email",
                        "value": "example@example.com"
                    }
                ],
                "address": [
                    {
                        "line": ["Example Medical Practice", "Example Street"],
                        "city": "Example City",
                        "postalCode": "AB12 3CD",
                        "country": "ENGLAND"
                    }
                ]
            },
            "search": {
                "mode": "match"
            }
        },
        {
            "fullUrl": "https://api.service.nhs.uk/FHIR/R4/Endpoint/1b62110d-4db5-4230-bf37-cbe948aecf76",
            "resource": {
                "resourceType": "Endpoint",
                "id": "1b62110d-4db5-4230-bf37-cbe948aecf76",
                "extension": [
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganizationEndpointOrder",
                        "valueInteger": 1
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointCompression",
                        "valueBoolean": False
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-EndpointBusinessScenario",
                        "valueCode": "primary-recipient"
                    }
                ],
                "status": "active",
                "connectionType": {
                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-EndpointConnection",
                    "code": "email"
                },
                "managingOrganization": {
                    "reference": "Organization/04393ec4-198f-42dd-9507-f4fa5e9ebf96"
                },
                "payloadType": [
                    {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/ValueSet/endpoint-payload-type",
                                "code": "urn:nhs-itk:interaction:primaryGeneralPractitionerRecipientNHS111CDADocument-v2-0"
                            }
                        ]
                    }
                ],
                "payloadMimeType": ["application/pdf"],
                "address": "dummy-endpoint-email@nhs.net"
            },
            "search": {
                "mode": "include"
            }
        }
    ]
}

PUT_SUCCESS_RESPONSE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "information",
            "code": "success",
            "diagnostics": "Organisation updated successfully"
        }
    ]
}

INVALID_IDENTIFIER_VALUE_RESPONSE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "invalid",
            "diagnostics": "Invalid identifier value: ODS code 'ABC' must follow format ^[A-Za-z0-9]{5,12}$"
        }
    ]
}

INVALID_IDENTIFIER_SYSTEM_RESPONSE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "invalid",
            "diagnostics": "Invalid identifier system 'foo' - expected 'odsOrganisationCode'"
        }
    ]
}

GET_NOT_FOUND_RESPONSE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "not-found",
            "diagnostics": "Organisation with ODS code 'DEF456' not found"
        }
    ]
}

PUT_NOT_FOUND_RESPONSE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "error",
            "code": "not-found",
            "diagnostics": "Organisation not found."
        }
    ]
}

INTERNAL_SERVER_ERROR_RESPONSE = {
    "resourceType": "OperationOutcome",
    "issue": [
        {
            "severity": "fatal",
            "code": "exception",
            "details": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                        "code": "exception",
                        "display": "Exception"
                    }
                ],
                "text": "An unexpected error occurred: please try again later."
            },
            "diagnostics": "please try again later."
        }
    ]
}
