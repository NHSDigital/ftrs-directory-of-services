import json
import os

MOCK_FOLDER = "responses/organizations"

def load_mock_response(ods_code: str):
    file_path = os.path.join(MOCK_FOLDER, f"{ods_code}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return None

def lambda_handler(event, context):
    path = event.get("rawPath") or event.get("path")
    if path in ("/ping", "/health"):
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "OK"})
        }

    query = event.get("queryStringParameters") or {}
    identifier = query.get("identifier", "")

    ods_code = None
    if "|" in identifier:
        _, ods_code = identifier.split("|", 1)

    if ods_code:
        response_body = load_mock_response(ods_code)

    if not ods_code or not response_body:
        response_body = {"resourceType": "Bundle", "type": "searchset", "total": 0, "entry": []}

    return {
        "statusCode": 200,
        "body": json.dumps(response_body)
    }
