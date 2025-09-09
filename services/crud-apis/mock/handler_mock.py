import json
from typing import Dict


def lambda_handler(event: Dict[str, object], context: object) -> Dict[str, object]:
    response = {
        "resourceType": "Organization",
        "id": "mock-org",
        "name": "Mock Organization",
        "telecom": [
            {"system": "phone", "value": "01234 567890"}
        ],
        "type": [
            {"text": "GP Practice"}
        ],
        "active": True
    }
    return {
        "statusCode": 200,
        "body": json.dumps(response),
        "headers": {"Content-Type": "application/json"}
    }
