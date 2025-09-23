@test-db-fixture @db-dos @dynamodb
Feature: Test Database Fixtures
  As a test developer
  I want to verify that database fixtures are working correctly
  So that I can use them in my tests

  Scenario: Test DoS database fixture connectivity
    Given the DoS database fixture is available
    Then I should be able to query the database

  Scenario: Test DynamoDB fixture connectivity
    Given the DynamoDB fixture is available
    Then I should be able to access DynamoDB tables

  Scenario: Test both fixtures together
    Given the DoS database fixture is available
    And the DynamoDB fixture is available
    Then both database connections should work
