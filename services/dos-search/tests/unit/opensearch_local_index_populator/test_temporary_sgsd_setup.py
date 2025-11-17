from unittest.mock import ANY, MagicMock, patch

from opensearch_local_index_populator.temporary_sgsd_setup import (
    connect_to_dynamodb,
    connect_to_opensearch,
    convert_dynamodb_format,
    initialise_index,
    main,
    scan_dynamodb_table,
)


# Test connect_to_dynamodb
@patch("boto3.client")
def test_connect_to_dynamodb(mock_boto_client):
    mock_client = MagicMock()
    mock_client.list_tables.return_value = {"TableNames": ["test_table"]}
    mock_boto_client.return_value = mock_client

    client = connect_to_dynamodb("http://localhost:8000")
    assert client == mock_client
    mock_client.list_tables.assert_called_once()


# Test connect_to_opensearch
@patch("opensearch_local_index_populator.temporary_sgsd_setup.OpenSearch")
def test_connect_to_opensearch(mock_opensearch):
    mock_client = MagicMock()
    mock_client.info.return_value = {"cluster_name": "test_cluster"}
    mock_opensearch.return_value = mock_client

    client = connect_to_opensearch("http://localhost:9200")
    assert client == mock_client
    mock_client.info.assert_called_once()


# Test initialise_index
def test_initialise_index():
    mock_client = MagicMock()
    initialise_index(mock_client, "temporary_sgsd_index")
    mock_client.indices.delete.assert_called_with(
        index="temporary_sgsd_index", ignore=[400, 404]
    )
    mock_client.indices.create.assert_called_with(
        index="temporary_sgsd_index", body=ANY, ignore=400
    )


# Test scan_dynamodb_table
def test_scan_dynamodb_table():
    mock_client = MagicMock()
    mock_client.scan.side_effect = [
        {"Items": [{"id": {"S": "1"}}], "LastEvaluatedKey": {"id": {"S": "1"}}},
        {"Items": [{"id": {"S": "2"}}]},
    ]
    result = scan_dynamodb_table(mock_client, "test_table", ["id"])
    assert len(result) == 2
    assert result[0]["id"]["S"] == "1"
    assert result[1]["id"]["S"] == "2"


# Test convert_dynamodb_format
def test_convert_dynamodb_format():
    data = [
        {
            "M": {
                "sg": {"M": {"codeID": {"N": "1175"}}},
                "sd": {"M": {"codeID": {"N": "4765"}}},
            }
        }
    ]
    result = convert_dynamodb_format(data)
    assert result == [{"sg": 1175, "sd": 4765}]


# Test main (integration)
@patch("opensearch_local_index_populator.temporary_sgsd_setup.connect_to_dynamodb")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.connect_to_opensearch")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.initialise_index")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.scan_dynamodb_table")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.convert_dynamodb_format")
def test_main(mock_convert, mock_scan, mock_init, mock_opensearch, mock_dynamo):
    mock_dynamo.return_value = MagicMock()
    mock_opensearch.return_value = MagicMock()
    mock_scan.return_value = [
        {
            "id": {"S": "1"},
            "field": {"S": "test"},
            "symptomGroupSymptomDiscriminators": {"L": []},
        }
    ]
    mock_convert.return_value = [{"sg": 1175, "sd": 4765}]

    main()

    mock_init.assert_called_once()
    mock_scan.assert_called_once()
    mock_convert.assert_called_once()
    mock_opensearch.return_value.index.assert_called_once()
