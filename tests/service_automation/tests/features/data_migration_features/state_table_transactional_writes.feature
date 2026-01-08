@data-migration
Feature: FTRS-1370 - Store migrated records in DynamoDB state table
  As a data migration pipeline
  I want to store all migrated records atomically with state information
  So that I can ensure data integrity and track migration history

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  @insert-operation @transactional-writes
  Scenario: Insert operation - Create new service with state record using TransactWriteItems
    Given a 'Service' exists called 'TestGPPracticeInsert' in DoS with attributes:
      | key          | value                                    |
      | id           | 400000                                   |
      | uid          | 400000                                   |
      | name         | TestGPPracticeInsert                     |
      | publicname   | New Surgery for Insert Test              |
      | typeid       | 100                                      |
      | statusid     | 1                                        |
      | odscode      | X12345                                   |
      | createdtime  | 2024-01-01 10:00:00                      |
      | modifiedtime | 2024-01-01 10:00:00                      |
      | postcode     | SW1A 1AA                                 |
      | address      | Westminster                              |
      | town         | London                                   |
      | web          | https://www.nhs.uk/                      |
      | email        | test@nhs.net                             |
      | publicphone  | 0300 311 22 33                           |
    When a record does not exist in the state table for key "services#400000"
    And a single service migration is run for ID '400000'
    Then the pipeline treats the record as an 'insert' operation
    And the pipeline sends a single TransactWriteItems operation
    And the organisation, location, healthcare service and state record is created
    And the state table contains a record for key "services#400000" with version 1
    And the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors

  @update-operation @skip-existing
  Scenario: Update operation - Skip when state record exists
    Given a 'Service' exists called 'TestGPPracticeUpdate' in DoS with attributes:
      | key          | value                                    |
      | id           | 400001                                   |
      | uid          | 400001                                   |
      | name         | TestGPPracticeUpdate                     |
      | publicname   | Existing Surgery for Update Test         |
      | typeid       | 100                                      |
      | statusid     | 1                                        |
      | odscode      | X12346                                   |
      | createdtime  | 2024-01-01 10:00:00                      |
      | modifiedtime | 2024-01-01 10:00:00                      |
      | postcode     | SW1A 2BB                                 |
      | address      | Whitehall                                |
      | town         | London                                   |
      | web          | https://www.nhs.uk/                      |
      | email        | test2@nhs.net                            |
      | publicphone  | 0300 311 22 44                           |
    When a single service migration is run for ID '400001'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    And the state table contains a record for key "services#400001" with version 1
    When a single service migration is run for ID '400001'
    Then the pipeline treats the record as an 'update' operation
    And the pipeline logs "State record found for Service ID 400001, Skipping now..."
    And the metrics should show 0 migrated records for the second run

  @state-table-structure
  Scenario: Verify state table record structure after migration
    Given a 'Service' exists called 'TestGPPracticeStructure' in DoS with attributes:
      | key          | value                                    |
      | id           | 400002                                   |
      | uid          | 400002                                   |
      | name         | TestGPPracticeStructure                  |
      | publicname   | Surgery for Structure Test               |
      | typeid       | 100                                      |
      | statusid     | 1                                        |
      | odscode      | X12347                                   |
      | createdtime  | 2024-01-01 10:00:00                      |
      | modifiedtime | 2024-01-01 10:00:00                      |
      | postcode     | SW1A 3CC                                 |
      | address      | Downing Street                           |
      | town         | London                                   |
      | web          | https://www.nhs.uk/                      |
      | email        | test3@nhs.net                            |
      | publicphone  | 0300 311 22 55                           |
    When a single service migration is run for ID '400002'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    And the state table record for "services#400002" contains all required fields
    And the state table record for "services#400002" has valid organisation_id
    And the state table record for "services#400002" has valid location_id
    And the state table record for "services#400002" has valid healthcare_service_id
