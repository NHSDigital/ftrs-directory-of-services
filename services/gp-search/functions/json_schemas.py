# currently validates only on ods code from input event
INPUT_EVENT = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "title": "Input Event",
    "required": ["odsCode"],
    "properties": {
        "odsCode": {
            "type": "string",
            "title": "ODS code",
            "examples": ["ABC123"],
            "pattern": "^[A-Z0-9]+$",
            "minLength": 5,
            "maxLength": 12,
        },
    },
}
