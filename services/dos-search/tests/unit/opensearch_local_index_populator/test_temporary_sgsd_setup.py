from unittest.mock import MagicMock, patch

from opensearch_local_index_populator.temporary_sgsd_setup import (
    connect_to_dynamodb,
    connect_to_opensearch,
    convert_dynamodb_format,
    index_definition,
    initialise_index,
    main,
    scan_dynamodb_table,
)


# Test connect_to_dynamodb
@patch("builtins.print")
@patch("boto3.client")
def test_connect_to_dynamodb(mock_boto_client, mock_print):
    mock_client = MagicMock()
    mock_client.list_tables.return_value = {"TableNames": ["test_table"]}
    mock_boto_client.return_value = mock_client

    client = connect_to_dynamodb("http://localhost:8000")
    assert client == mock_client
    mock_boto_client.assert_called_once_with(
        "dynamodb", endpoint_url="http://localhost:8000"
    )
    mock_client.list_tables.assert_called_once()
    mock_print.assert_called_once_with({"TableNames": ["test_table"]})


# Test connect_to_opensearch
@patch("builtins.print")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.OpenSearch")
def test_connect_to_opensearch(mock_opensearch, mock_print):
    mock_client = MagicMock()
    mock_client.info.return_value = {"cluster_name": "test_cluster"}
    mock_opensearch.return_value = mock_client

    client = connect_to_opensearch("http://localhost:9200")
    assert client == mock_client
    mock_client.info.assert_called_once()
    mock_print.assert_called_once_with({"cluster_name": "test_cluster"})


def test_connect_to_opensearch_parses_url_correctly():
    """Test that connect_to_opensearch correctly parses host and port from URL"""
    with patch(
        "opensearch_local_index_populator.temporary_sgsd_setup.OpenSearch"
    ) as mock_os:
        mock_client = MagicMock()
        mock_client.info.return_value = {}
        mock_os.return_value = mock_client

        connect_to_opensearch("http://myhost:8080")

        # Verify OpenSearch was called with correct host and port
        call_kwargs = mock_os.call_args[1]
        assert call_kwargs["hosts"] == [{"host": "myhost", "port": 8080}]
        assert call_kwargs["http_compress"] is True
        assert call_kwargs["use_ssl"] is False
        assert call_kwargs["verify_certs"] is False


# Test initialise_index
@patch("builtins.print")
def test_initialise_index(mock_print):
    mock_client = MagicMock()
    initialise_index(mock_client, "temporary_sgsd_index")
    mock_client.indices.delete.assert_called_with(
        index="temporary_sgsd_index", ignore=[400, 404]
    )
    mock_client.indices.create.assert_called_with(
        index="temporary_sgsd_index", body=index_definition, ignore=400
    )
    assert mock_print.call_count == 2
    mock_print.assert_any_call("Deleted existing temporary_sgsd_index if it existed.")
    mock_print.assert_any_call("Created temporary_sgsd_index.")


# Test scan_dynamodb_table
@patch("builtins.print")
def test_scan_dynamodb_table(mock_print):
    mock_client = MagicMock()
    mock_client.scan.side_effect = [
        {"Items": [{"id": {"S": "1"}}], "LastEvaluatedKey": {"id": {"S": "1"}}},
        {"Items": [{"id": {"S": "2"}}]},
    ]
    result = scan_dynamodb_table(mock_client, "test_table", ["id"])
    assert len(result) == 2
    assert result[0]["id"]["S"] == "1"
    assert result[1]["id"]["S"] == "2"
    mock_print.assert_called_once_with("processing loop: 0")


def test_scan_dynamodb_table_single_page():
    """Test scan_dynamodb_table with only one page of results (no pagination)"""
    mock_client = MagicMock()
    mock_client.scan.return_value = {"Items": [{"id": {"S": "1"}}, {"id": {"S": "2"}}]}

    result = scan_dynamodb_table(mock_client, "test_table", ["id"])

    assert len(result) == 2
    assert result[0]["id"]["S"] == "1"
    assert result[1]["id"]["S"] == "2"
    mock_client.scan.assert_called_once()


@patch("builtins.print")
def test_scan_dynamodb_table_multiple_pages(mock_print):
    """Test scan_dynamodb_table with multiple pages of pagination"""
    mock_client = MagicMock()
    mock_client.scan.side_effect = [
        {"Items": [{"id": {"S": "1"}}], "LastEvaluatedKey": {"id": {"S": "1"}}},
        {"Items": [{"id": {"S": "2"}}], "LastEvaluatedKey": {"id": {"S": "2"}}},
        {"Items": [{"id": {"S": "3"}}], "LastEvaluatedKey": {"id": {"S": "3"}}},
        {"Items": [{"id": {"S": "4"}}]},
    ]

    result = scan_dynamodb_table(mock_client, "test_table", ["id"])

    assert len(result) == 4
    assert mock_client.scan.call_count == 4
    # Verify print was called for each pagination loop (3 times, not for the last page)
    assert mock_print.call_count == 3


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


def test_convert_dynamodb_format_multiple_items():
    """Test convert_dynamodb_format with multiple items"""
    data = [
        {
            "M": {
                "sg": {"M": {"codeID": {"N": "1175"}}},
                "sd": {"M": {"codeID": {"N": "4765"}}},
            }
        },
        {
            "M": {
                "sg": {"M": {"codeID": {"N": "2000"}}},
                "sd": {"M": {"codeID": {"N": "3000"}}},
            }
        },
    ]

    result = convert_dynamodb_format(data)

    assert len(result) == 2
    assert result[0] == {"sg": 1175, "sd": 4765}
    assert result[1] == {"sg": 2000, "sd": 3000}


def test_convert_dynamodb_format_empty_list():
    """Test convert_dynamodb_format with empty list"""
    result = convert_dynamodb_format([])
    assert result == []


def test_index_definition_structure():
    """Test that index_definition has the correct structure"""
    assert "mappings" in index_definition
    assert "properties" in index_definition["mappings"]
    assert "id" in index_definition["mappings"]["properties"]
    assert "field" in index_definition["mappings"]["properties"]
    assert "sgsds" in index_definition["mappings"]["properties"]


# Test main (integration)
@patch("builtins.print")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.connect_to_dynamodb")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.connect_to_opensearch")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.initialise_index")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.scan_dynamodb_table")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.convert_dynamodb_format")
def test_main(
    mock_convert, mock_scan, mock_init, mock_opensearch, mock_dynamo, mock_print
):
    mock_dynamo.return_value = MagicMock()
    mock_os_client = MagicMock()
    mock_opensearch.return_value = mock_os_client
    mock_scan.return_value = [
        {
            "id": {"S": "1"},
            "field": {"S": "test"},
            "symptomGroupSymptomDiscriminators": {"L": []},
        }
    ]
    mock_convert.return_value = [{"sg": 1175, "sd": 4765}]

    main()

    mock_dynamo.assert_called_once_with("http://localhost:8000")
    mock_opensearch.assert_called_once_with("http://localhost:9200")
    mock_init.assert_called_once_with(mock_os_client, "temporary_sgsd_index")
    mock_scan.assert_called_once_with(
        mock_dynamo.return_value,
        "ftrs-dos-local-database-healthcare-service",
        ["id", "field", "symptomGroupSymptomDiscriminators"],
    )
    mock_convert.assert_called_once_with([])
    mock_os_client.index.assert_called_once()
    mock_print.assert_any_call("Indexing record ID: 1")


@patch("builtins.print")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.connect_to_dynamodb")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.connect_to_opensearch")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.initialise_index")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.scan_dynamodb_table")
@patch("opensearch_local_index_populator.temporary_sgsd_setup.convert_dynamodb_format")
def test_main_indexes_multiple_records(
    mock_convert, mock_scan, mock_init, mock_opensearch, mock_dynamo, mock_print
):
    """Test that main indexes multiple records correctly"""
    mock_os_client = MagicMock()
    mock_opensearch.return_value = mock_os_client
    mock_scan.return_value = [
        {
            "id": {"S": "1"},
            "field": {"S": "field1"},
            "symptomGroupSymptomDiscriminators": {"L": []},
        },
        {
            "id": {"S": "2"},
            "field": {"S": "field2"},
            "symptomGroupSymptomDiscriminators": {"L": []},
        },
    ]
    mock_convert.return_value = [{"sg": 1175, "sd": 4765}]

    main()

    assert mock_os_client.index.call_count == 2
    # Verify the index calls contain the expected IDs
    calls = mock_os_client.index.call_args_list
    assert calls[0][1]["id"] == "1|field1"
    assert calls[1][1]["id"] == "2|field2"
