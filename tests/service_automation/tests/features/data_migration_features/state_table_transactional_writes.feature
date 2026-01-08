@data-migration
Feature: FTRS-1370 - Store migrated records in DynamoDB state table

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  @insert-operation @transactional-writes
  Scenario: Insert operation - Create new service with state record using TransactWriteItems
    Given a 'Service' exists called 'TestGPPracticeInsert' in DoS with attributes:
      | key                 | value                                    |
      | id                  | 400000                                   |
      | uid                 | 400000                                   |
      | name                | TestGPPracticeInsert                     |
      | publicname          | New Surgery for Insert Test              |
      | typeid              | 100                                      |
      | statusid            | 1                                        |
      | odscode             | A12348                                   |
      | createdtime         | 2024-01-01 10:00:00                      |
      | modifiedtime        | 2024-01-01 10:00:00                      |
      | openallhours        | false                                    |
      | restricttoreferrals | false                                    |
      | postcode            | SW1A 1AA                                 |
      | address             | Westminster                              |
      | town                | London                                   |
      | web                 | https://www.nhs.uk/                      |
      | email               | test@nhs.net                             |
      | publicphone         | 0300 311 22 33                           |
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
      | key                 | value                                    |
      | id                  | 400001                                   |
      | uid                 | 400001                                   |
      | name                | TestGPPracticeUpdate                     |
      | publicname          | Existing Surgery for Update Test         |
      | typeid              | 100                                      |
      | statusid            | 1                                        |
      | odscode             | A12349                                   |
      | createdtime         | 2024-01-01 10:00:00                      |
      | modifiedtime        | 2024-01-01 10:00:00                      |
      | openallhours        | false                                    |
      | restricttoreferrals | false                                    |
      | postcode            | SW1A 2BB                                 |
      | address             | Whitehall                                |
      | town                | London                                   |
      | web                 | https://www.nhs.uk/                      |
      | email               | test2@nhs.net                            |
      | publicphone         | 0300 311 22 44                           |
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
      | key                 | value                                    |
      | id                  | 400002                                   |
      | uid                 | 400002                                   |
      | name                | TestGPPracticeStructure                  |
      | publicname          | Surgery for Structure Test               |
      | typeid              | 100                                      |
      | statusid            | 1                                        |
      | odscode             | A12350                                   |
      | createdtime         | 2024-01-01 10:00:00                      |
      | modifiedtime        | 2024-01-01 10:00:00                      |
      | openallhours        | false                                    |
      | restricttoreferrals | false                                    |
      | postcode            | SW1A 3CC                                 |
      | address             | Downing Street                           |
      | town                | London                                   |
      | web                 | https://www.nhs.uk/                      |
      | email               | test3@nhs.net                            |
      | publicphone         | 0300 311 22 55                           |
    When a single service migration is run for ID '400002'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    And the state table record for "services#400002" contains all required fields
    And the state table record for "services#400002" has valid organisation_id
    And the state table record for "services#400002" has valid location_id
    And the state table record for "services#400002" has valid healthcare_service_id

  @conflict-detection @organisation-exists
  Scenario: Conflict detection - Organisation already exists
    Given a 'Service' exists called 'TestGPPracticeConflictOrg' in DoS with attributes:
      | key                 | value                                    |
      | id                  | 400003                                   |
      | uid                 | 400003                                   |
      | name                | TestGPPracticeConflictOrg                |
      | publicname          | Surgery for Org Conflict Test            |
      | typeid              | 100                                      |
      | statusid            | 1                                        |
      | odscode             | A12351                                   |
      | createdtime         | 2024-01-01 10:00:00                      |
      | modifiedtime        | 2024-01-01 10:00:00                      |
      | openallhours        | false                                    |
      | restricttoreferrals | false                                    |
      | postcode            | SW1A 4DD                                 |
      | address             | Parliament Square                        |
      | town                | London                                   |
      | web                 | https://www.nhs.uk/                      |
      | email               | test4@nhs.net                            |
      | publicphone         | 0300 311 22 66                           |
    When a record does not exist in the state table for key "services#400003"
    And a record exists in the Organisation table matching the transformed organisation ID for service 400003
    And a single service migration is run for ID '400003'
    Then the pipeline treats the record as an 'insert' operation
    And the DynamoDB TransactWriteItems request is rejected due to ConditionalCheckFailed
    And the pipeline logs "One or more items exist for  Service ID 400003"
    And the migration records an error for service ID 400003

  @conflict-detection @location-exists
  Scenario: Conflict detection - Location already exists
    Given a 'Service' exists called 'TestGPPracticeConflictLoc' in DoS with attributes:
      | key                 | value                                    |
      | id                  | 400004                                   |
      | uid                 | 400004                                   |
      | name                | TestGPPracticeConflictLoc                |
      | publicname          | Surgery for Location Conflict Test       |
      | typeid              | 100                                      |
      | statusid            | 1                                        |
      | odscode             | A12352                                   |
      | createdtime         | 2024-01-01 10:00:00                      |
      | modifiedtime        | 2024-01-01 10:00:00                      |
      | openallhours        | false                                    |
      | restricttoreferrals | false                                    |
      | postcode            | SW1A 5EE                                 |
      | address             | Victoria Street                          |
      | town                | London                                   |
      | web                 | https://www.nhs.uk/                      |
      | email               | test5@nhs.net                            |
      | publicphone         | 0300 311 22 77                           |
    When a record does not exist in the state table for key "services#400004"
    And a record exists in the Location table matching the transformed location ID for service 400004
    And a single service migration is run for ID '400004'
    Then the pipeline treats the record as an 'insert' operation
    And the DynamoDB TransactWriteItems request is rejected due to ConditionalCheckFailed
    And the pipeline logs "One or more items exist for  Service ID 400004"
    And the migration records an error for service ID 400004

  @conflict-detection @healthcare-service-exists
  Scenario: Conflict detection - Healthcare Service already exists
    Given a 'Service' exists called 'TestGPPracticeConflictHCS' in DoS with attributes:
      | key                 | value                                    |
      | id                  | 400005                                   |
      | uid                 | 400005                                   |
      | name                | TestGPPracticeConflictHCS                |
      | publicname          | Surgery for HCS Conflict Test            |
      | typeid              | 100                                      |
      | statusid            | 1                                        |
      | odscode             | A12353                                   |
      | createdtime         | 2024-01-01 10:00:00                      |
      | modifiedtime        | 2024-01-01 10:00:00                      |
      | openallhours        | false                                    |
      | restricttoreferrals | false                                    |
      | postcode            | SW1A 6FF                                 |
      | address             | Buckingham Palace Road                   |
      | town                | London                                   |
      | web                 | https://www.nhs.uk/                      |
      | email               | test6@nhs.net                            |
      | publicphone         | 0300 311 22 88                           |
    When a record does not exist in the state table for key "services#400005"
    And a record exists in the Healthcare Service table matching the transformed healthcare service ID for service 400005
    And a single service migration is run for ID '400005'
    Then the pipeline treats the record as an 'insert' operation
    And the DynamoDB TransactWriteItems request is rejected due to ConditionalCheckFailed
    And the pipeline logs "One or more items exist for  Service ID 400005"
    And the migration records an error for service ID 400005
