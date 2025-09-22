import json
import os
from typing import Dict, Optional

MOCK_RESPONSES = os.path.join(os.path.dirname(__file__), "responses")

def load_response(filename: str) -> Optional[Dict]:
    path = os.path.join(MOCK_RESPONSES, filename)
    print(f"Loading response from: {path}")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def handler(event: Dict[str, object], context: object) -> Dict[str, object]:
    path = event.get("rawPath") or event.get("path")
    query = event.get("queryStringParameters") or {}
    headers = event.get("headers") or {}

    status_code = 404
    response_body = {"error": "Not found"}
    content_type = "application/json"

    if path in ("/ping", "/health"):
        status_code = 200
        response_body = {"status": "OK"}
    else:
        auth_header = headers.get("apikey")
        if not auth_header:
            status_code = 401
            response_body = load_response("401-example.json")
            content_type = "application/fhir+json"
        elif auth_header == "invalid":
            status_code = 403
            response_body = load_response("403-example.json")
            content_type = "application/fhir+json"
        elif path == "/Organization":
            identifier = query.get("identifier", "")
            revinclude = query.get("_revinclude", "")

            if identifier.startswith("foo|"):
                status_code = 400
                response_body = load_response("invalid-identifier-system.json")
                content_type = "application/fhir+json"
            elif identifier.startswith("odsOrganisationCode|") and not revinclude:
                status_code = 400
                response_body = load_response("missing-revinclude.json")
                content_type = "application/fhir+json"
            elif identifier.startswith("odsOrganisationCode|") and revinclude == "Endpoint:organization":
                status_code = 200
                response_body = load_response("200-example.json")
                content_type = "application/fhir+json"
            elif identifier.startswith("odsOrganisationCode|ABC") and revinclude == "Endpoint:organization":
                status_code = 400
                response_body = load_response("invalid-identifier-value.json")
                content_type = "application/fhir+json"
            else:
                status_code = 500
                response_body = load_response("500-example.json")
                content_type = "application/fhir+json"

    return {
        "statusCode": status_code,
        "body": json.dumps(response_body),
        "headers": {"Content-Type": content_type}
    }
