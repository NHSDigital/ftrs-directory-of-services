import pytest
from pytest_bdd import given, when, then, scenarios
from sqlalchemy import text


# Load all scenarios from the feature file
scenarios('./data_migration_features/database_dynamodb.feature')


@given("the DoS database fixture is available")
def given_dos_db_available(dos_db):
    """Verify DoS database fixture is working."""
    assert dos_db is not None, "DoS database fixture should be available"


@given("the DynamoDB fixture is available")
def given_dynamodb_available(dynamodb):
    """Verify the DynamoDB fixture is working."""
    assert dynamodb is not None, "DynamoDB fixture should be available"
    assert "client" in dynamodb, "DynamoDB fixture should have client"
    assert "resource" in dynamodb, "DynamoDB fixture should have resource"


@then("I should be able to query the database")
def then_can_query_dos_db(dos_db):
    """Test that we can execute queries against the DoS database."""
    # Simple test query - just verify the connection works
    result = dos_db.execute(text("SELECT 1 as test_value"))
    row = result.fetchone()
    assert row[0] == 1, "Should be able to execute simple query"

    # Test that we can query the service table
    result = dos_db.execute(text("SELECT COUNT(*) FROM pathwaysdos.services"))
    row = result.fetchone()
    assert row[0] == 3, "Should have 3 seeded services"


@then("I should be able to access DynamoDB tables")
def then_can_access_dynamodb_tables(dynamodb):
    """Test that we can access DynamoDB tables."""
    client = dynamodb["client"]

    # List tables to verify connection
    response = client.list_tables()
    assert "TableNames" in response, "Should be able to list DynamoDB tables"

    # Verify our test tables exist
    table_names = response["TableNames"]
    expected_tables = ["organisation", "location", "healthcare-service"]

    for table_name in expected_tables:
        assert table_name in table_names, f"Expected table '{table_name}' should exist"


@then("both database connections should work")
def then_both_connections_work(dos_db, dynamodb):
    """Test that both database fixtures work together."""
    # Test DoS DB
    dos_result = dos_db.execute(text("SELECT 1 as test_value"))
    dos_row = dos_result.fetchone()
    assert dos_row[0] == 1, "DoS database should work"

    client = dynamodb["client"]
    dynamo_response = client.list_tables()
    assert "TableNames" in dynamo_response, "DynamoDB should work"

    assert True, "Both database fixtures are working correctly"


# Optional: Add a cleanup step that can be used in BDD scenarios
@pytest.fixture(autouse=True, scope="function")
def cleanup_after_scenario():
    """Automatically cleanup after each scenario."""
    yield
    # Any additional cleanup logic can go here
    # The fixture cleanup will handle DB connections automatically
