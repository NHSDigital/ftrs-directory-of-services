dynamodb_tables = [
    {
        "TableName": "organisation",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "field", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "field", "AttributeType": "S"},
            {
                "AttributeName": "identifier_ODS_ODSCode",
                "AttributeType": "S",
            },
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "OdsCodeValueIndex",
                "KeySchema": [
                    {
                        "AttributeName": "identifier_ODS_ODSCode",
                        "KeyType": "HASH",
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        "BillingMode": "PAY_PER_REQUEST"
    },
    {
        "TableName": "healthcare-service",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "field", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "field", "AttributeType": "S"},
            {"AttributeName": "providedBy", "AttributeType": "S"},
            {"AttributeName": "location", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "ProvidedByValueIndex",
                "KeySchema": [
                    {
                        "AttributeName": "providedBy",
                        "KeyType": "HASH",
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "LocationIndex",
                "KeySchema": [
                    {
                        "AttributeName": "location",
                        "KeyType": "HASH",
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST"
    },
    {
        "TableName": "location",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "field", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "field", "AttributeType": "S"},
            {"AttributeName": "managingOrganisation", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "ManagingOrganisationIndex",
                "KeySchema": [
                    {
                        "AttributeName": "managingOrganisation",
                        "KeyType": "HASH",
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        "BillingMode": "PAY_PER_REQUEST"
    },
    {
        "TableName": "triage-code",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "field", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "field", "AttributeType": "S"},
            {"AttributeName": "codeType", "AttributeType": "S"},
            {"AttributeName": "codeID", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "CodeTypeIndex",
                "KeySchema": [
                    {
                        "AttributeName": "codeType",
                        "KeyType": "HASH",
                    },
                    {
                        "AttributeName": "id",
                        "KeyType": "RANGE",
                    },
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],

        "BillingMode": "PAY_PER_REQUEST"
    }
]
