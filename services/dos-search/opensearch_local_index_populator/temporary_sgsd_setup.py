import json

import boto3
from opensearchpy import OpenSearch

index_definition = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "field": {"type": "text"},
            "sgsds": {
                "type": "nested",
                "properties": {
                    "sg": {"type": "integer"},
                    "sd": {"type": "integer"},
                },
            },
        }
    }
}


def connect_to_dynamodb(endpoint_url: str) -> boto3.client:
    dynamodb_client = boto3.client("dynamodb", endpoint_url=endpoint_url)
    print(dynamodb_client.list_tables())
    return dynamodb_client


def connect_to_opensearch(url: str) -> OpenSearch:
    host = url.split(":")[1].replace("//", "")
    port = int(url.split(":")[2])
    opensearch_client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_compress=True,  # enables gzip compression for request bodies
        # http_auth=auth,
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        # ca_certs=ca_certs_path
    )
    print(opensearch_client.info())
    return opensearch_client


def initialise_index(opensearch_client: OpenSearch, index_name: str) -> None:
    # Delete the index if it exists so that we refresh it completely when this script it run
    opensearch_client.indices.delete(index=index_name, ignore=[400, 404])
    print("Deleted existing temporary_sgsd_index if it existed.")

    # Create the index
    opensearch_client.indices.create(
        index="temporary_sgsd_index", body=index_definition, ignore=400
    )
    print("Created temporary_sgsd_index.")


def scan_dynamodb_table(
    dynamodb_client: boto3.client, table_name: str, fields: list[str]
) -> list[dict]:
    response = dynamodb_client.scan(
        TableName=table_name, ProjectionExpression=", ".join(fields), Limit=10
    )
    items = response.get("Items", [])

    i = 0

    while "LastEvaluatedKey" in response:
        response = dynamodb_client.scan(
            TableName=table_name,
            ExclusiveStartKey=response["LastEvaluatedKey"],
            ProjectionExpression=", ".join(fields),
            Limit=10,
        )
        items.extend(response.get("Items", []))

        print(f"processing loop: {i}")
        i += 1

    return items


def convert_dynamodb_format(data: list[dict]) -> list[dict]:
    """
    Converts DynamoDB nested attribute format into simplified list of dicts
    like [{'sg': 1175, 'sd': 4765}, ...].

    :param data: List of DynamoDB items in the given format
    :return: List of dictionaries with 'sg' and 'sd' keys
    """
    result = []
    for item in data:
        # Navigate through the nested structure
        sg_code = int(item["M"]["sg"]["M"]["codeID"]["N"])
        sd_code = int(item["M"]["sd"]["M"]["codeID"]["N"])

        result.append({"sg": sg_code, "sd": sd_code})

    return result


def main() -> None:
    index_name = "temporary_sgsd_index"

    # Connect to DynamoDB and OpenSearch
    dynamodb_client = connect_to_dynamodb(
        "http://localhost:8000"
    )  # Local DynamoDB endpoint based on docker
    opensearch_client = connect_to_opensearch(
        "http://localhost:9200"
    )  # Local openSearch endpoint based on docker

    # Initialise the OpenSearch index
    initialise_index(opensearch_client, index_name)

    # Scan the DynamoDB table to get all records
    records = scan_dynamodb_table(
        dynamodb_client,
        "ftrs-dos-local-database-healthcare-service",
        ["id", "field", "symptomGroupSymptomDiscriminators"],
    )

    # Transform records to match OpenSearch index structure
    records = [
        {
            "id": record["id"]["S"],
            "field": record["field"]["S"],
            "sgsds": convert_dynamodb_format(
                record["symptomGroupSymptomDiscriminators"]["L"]
            ),
        }
        for record in records
    ]

    # Index records into OpenSearch
    for record in records:
        print(f"Indexing record ID: {record['id']}")
        opensearch_client.index(
            index=index_name,
            id=f"{record['id']}|{record['field']}",
            body=json.dumps(record),
        )


if __name__ == "__main__":
    main()
