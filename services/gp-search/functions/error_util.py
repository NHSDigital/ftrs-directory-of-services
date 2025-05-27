from aws_lambda_powertools.utilities.validation import SchemaValidationError
from fhir.resources.R4B.operationoutcome import OperationOutcome


def create_resource_internal_server_error() -> OperationOutcome:
    return OperationOutcome.model_validate(
        {
            "id": "internal-server-error",
            "issue": [
                {
                    "severity": "error",
                    "code": "internal",
                    "details": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                                "code": "INTERNAL_SERVER_ERROR",
                                "display": "Internal server error occurred",
                            },
                        ]
                    },
                }
            ],
        }
    )


def create_resource_validation_error(
    exception: SchemaValidationError,
) -> OperationOutcome:
    # assumes that the exception is related to the ODS code format
    return OperationOutcome.model_validate(
        {
            "id": "ods-code-validation-error",
            "issue": [
                {
                    "severity": "error",
                    "code": "invalid",
                    "details": {
                        "coding": [
                            {
                                "system": "https://fhir.nhs.uk/CodeSystem/Spine-ErrorOrWarningCode",
                                "code": "INVALID_ODS_CODE_FORMAT",
                                "display": "Invalid ODS Code Format",
                            }
                        ],
                        "text": "The organization.identifier ODS code provided in the search parameter does not match the required format",
                    },
                    "diagnostics": exception.message,
                    "expression": [exception.name],
                },
            ],
        }
    )
