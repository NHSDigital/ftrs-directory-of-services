from ftrs_data_layer.client import get_dynamodb_client, get_dynamodb_resource


def test_get_dynamo_client_is_cached() -> None:
    client = get_dynamodb_client()
    assert client is not None

    second_client = get_dynamodb_client()
    assert client is second_client


def test_get_dynamo_resource_is_cached() -> None:
    resource = get_dynamodb_resource()
    assert resource is not None

    second_resource = get_dynamodb_resource()
    assert resource is second_resource
