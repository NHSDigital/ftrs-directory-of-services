from pytest_bdd import scenarios, given, when, then, parsers,scenario
import json

# scenarios("../features/data_migration_features/data_migration.feature")
@scenario('../features/data_migration_features/data_migration.feature', 'Hello world scenario for data migration')
def test_publish():
    pass

@given("the data migration system is ready")
def data_migration_system_ready():
    pass

@when("I run the hello world data migration test")
def run_hello_world_test():
    pass

@then("I see a hello world result")
def see_hello_world_result():
    print("Hello World!Data migration test ran successfully.")

def remove_expected_dynamic_fields(expected, dynamic_fields):
    for field in dynamic_fields:
        assert field in expected, f"Expected field '{field}' not found in item"
        del expected[field]

@then(parsers.parse("The '{table_name}' for service ID '{service_name}' has content:"))
def check_table_content_by_id(table_name, service_name,docstring, dynamodb):

    print(f"Checking content of table '{table_name}' for service ID '{service_name}'")
    print(docstring)
    """Verify the DynamoDB fixture is working."""
    assert dynamodb is not None, "DynamoDB fixture should be available"
    assert "client" in dynamodb, "DynamoDB fixture should have client"
    assert "resource" in dynamodb, "DynamoDB fixture should have resource"
    client = dynamodb["client"]
    dynamodb_resource = dynamodb["resource"]
    # List tables to verify connection
    response = client.list_tables()
    print (response)

    table = dynamodb_resource.Table('organisation')
    
    table.put_item(
    Item={
        "id": '12345',
        "field": 'document',
        "name": "test org",
        "createdDateTime": "2024-01-01T00:00:00Z",
        "modifiedDateTime": "2024-01-01T00:00:00"
    }
    )
    # Read an item by primary key
    response = table.get_item(
    Key={
        'id': '12345',
        'field':'document'
    }
    )
    print (response)
    assert 'Item' in response, "No item found under id"
    item = response['Item']
    dynamic_fields = ['createdDateTime', 'modifiedDateTime']
    expected = sorted(json.loads(docstring).items())
    actual = sorted(json.loads(json.dumps(item)).items())
    remove_expected_dynamic_fields(actual, dynamic_fields)
    assert expected == actual, f"Expected {expected}, but got {actual}"

