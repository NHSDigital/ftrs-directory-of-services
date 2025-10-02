Feature: Data Load and Schema Load Verification
  As a system administrator
  I want to verify that data has been migrated correctly
  So that I can ensure the system maintains data integrity

  @test-db-load-schema-data-migration
  Scenario: Verify servicetypes data is migrated correctly
    Given I have a database with migrated data
    When I query the "servicetypes" table
    Then the "servicetypes" table should have data

