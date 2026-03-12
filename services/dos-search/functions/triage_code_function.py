import json

DEFAULT_RESPONSE_HEADERS: dict[str, str] = {
    "Content-Type": "application/fhir+json",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Cache-Control": "no-store",
}


def lambda_handler(event: dict, context: object) -> dict:
    return {
        "statusCode": 501,
        "headers": DEFAULT_RESPONSE_HEADERS,
        "body": json.dumps(
            {
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "not-supported",
                        "diagnostics": "TriageCode endpoint is not implemented",
                    }
                ],
            }
        ),
    }
