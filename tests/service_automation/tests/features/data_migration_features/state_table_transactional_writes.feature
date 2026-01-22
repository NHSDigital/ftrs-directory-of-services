@data-migration
Feature: FTRS-1370 - Store migrated records in DynamoDB state table

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  @insert-operation @transactional-writes
  Scenario: Insert operation - Create new service with state record using TransactWriteItems
    Given a 'Service' exists called 'TestGPPracticeInsert' in DoS with attributes:
      | key                 | value                       |
      | id                  | 400000                      |
      | uid                 | 400000                      |
      | name                | TestGPPracticeInsert        |
      | publicname          | New Surgery for Insert Test |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | odscode             | A12348                      |
      | createdtime         | 2024-01-01 10:00:00         |
      | modifiedtime        | 2024-01-01 10:00:00         |
      | openallhours        | false                       |
      | restricttoreferrals | false                       |
      | postcode            | SW1A 1AA                    |
      | address             | Westminster                 |
      | town                | London                      |
      | web                 | https://www.nhs.uk/         |
      | email               | test@nhs.net                |
      | publicphone         | 0300 311 22 33              |
    When a record does not exist in the state table for key 'services#400000'
    And a single service migration is run for ID '400000'
    Then the pipeline treats the record as an 'insert' operation
    And the pipeline sends a single TransactWriteItems operation with 4 items
    And the organisation, location, healthcare service and state record is created
    And the state table contains a record for key 'services#400000' with version 1
    And the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errors

  @update-operation @skip-existing
  Scenario: Update operation - Skip when state record exists
    Given a 'Service' exists called 'TestGPPracticeUpdate' in DoS with attributes:
      | key                 | value                            |
      | id                  | 400001                           |
      | uid                 | 400001                           |
      | name                | TestGPPracticeUpdate             |
      | publicname          | Existing Surgery for Update Test |
      | typeid              | 100                              |
      | statusid            | 1                                |
      | odscode             | A12349                           |
      | createdtime         | 2024-01-01 10:00:00              |
      | modifiedtime        | 2024-01-01 10:00:00              |
      | openallhours        | false                            |
      | restricttoreferrals | false                            |
      | postcode            | SW1A 2BB                         |
      | address             | Whitehall                        |
      | town                | London                           |
      | web                 | https://www.nhs.uk/              |
      | email               | test2@nhs.net                    |
      | publicphone         | 0300 311 22 44                   |
    When a single service migration is run for ID '400001'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errors
    And the state table contains a record for key 'services#400001' with version 1
    When a single service migration is run for ID '400001'
    Then the pipeline treats the record as an 'update' operation
    And the metrics should show 0 inserted, 0 updated records for the second run

  @state-table-structure
  Scenario: Verify state table record structure after migration
    Given a 'Service' exists called 'TestGPPracticeStructure' in DoS with attributes:
      | key                 | value                      |
      | id                  | 400002                     |
      | uid                 | 400002                     |
      | name                | TestGPPracticeStructure    |
      | publicname          | Surgery for Structure Test |
      | typeid              | 100                        |
      | statusid            | 1                          |
      | odscode             | A12350                     |
      | createdtime         | 2024-01-01 10:00:00        |
      | modifiedtime        | 2024-01-01 10:00:00        |
      | openallhours        | false                      |
      | restricttoreferrals | false                      |
      | postcode            | SW1A 3CC                   |
      | address             | Downing Street             |
      | town                | London                     |
      | web                 | https://www.nhs.uk/        |
      | email               | test3@nhs.net              |
      | publicphone         | 0300 311 22 55             |
    When a single service migration is run for ID '400002'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errors
    And the state table record for "services#400002" contains all required fields
    And the state table record for "services#400002" has valid organisation_id
    And the state table record for "services#400002" has valid location_id
    And the state table record for "services#400002" has valid healthcare_service_id

  @conflict-detection @organisation-exists
  Scenario: Conflict detection - Organisation already exists
    Given a 'Service' exists called 'TestGPPracticeConflictOrg' in DoS with attributes:
      | key                 | value                         |
      | id                  | 400003                        |
      | uid                 | 400003                        |
      | name                | TestGPPracticeConflictOrg     |
      | publicname          | Surgery for Org Conflict Test |
      | typeid              | 100                           |
      | statusid            | 1                             |
      | odscode             | A12351                        |
      | createdtime         | 2024-01-01 10:00:00           |
      | modifiedtime        | 2024-01-01 10:00:00           |
      | openallhours        | false                         |
      | restricttoreferrals | false                         |
      | postcode            | SW1A 4DD                      |
      | address             | Parliament Square             |
      | town                | London                        |
      | web                 | https://www.nhs.uk/           |
      | email               | test4@nhs.net                 |
      | publicphone         | 0300 311 22 66                |
    When a record does not exist in the state table for key 'services#400003'
    And a record exists in the Organisation table matching the transformed organisation ID for service 400003
    And a single service migration is run for ID '400003'
    Then the pipeline treats the record as an 'insert' operation
    And the DynamoDB TransactWriteItems request is rejected due to ConditionalCheckFailed
    And the pipeline logs "DynamoDB Transaction Cancelled - one or more items failed to write"
    And the migration records an error for service ID 400003

  @conflict-detection @location-exists
  Scenario: Conflict detection - Location already exists
    Given a 'Service' exists called 'TestGPPracticeConflictLoc' in DoS with attributes:
      | key                 | value                              |
      | id                  | 400004                             |
      | uid                 | 400004                             |
      | name                | TestGPPracticeConflictLoc          |
      | publicname          | Surgery for Location Conflict Test |
      | typeid              | 100                                |
      | statusid            | 1                                  |
      | odscode             | A12352                             |
      | createdtime         | 2024-01-01 10:00:00                |
      | modifiedtime        | 2024-01-01 10:00:00                |
      | openallhours        | false                              |
      | restricttoreferrals | false                              |
      | postcode            | SW1A 5EE                           |
      | address             | Victoria Street                    |
      | town                | London                             |
      | web                 | https://www.nhs.uk/                |
      | email               | test5@nhs.net                      |
      | publicphone         | 0300 311 22 77                     |
    When a record does not exist in the state table for key 'services#400004'
    And a record exists in the Location table matching the transformed location ID for service 400004
    And a single service migration is run for ID '400004'
    Then the pipeline treats the record as an 'insert' operation
    And the DynamoDB TransactWriteItems request is rejected due to ConditionalCheckFailed
    And the pipeline logs "DynamoDB Transaction Cancelled - one or more items failed to write"
    And the migration records an error for service ID 400004

  @conflict-detection @healthcare-service-exists
  Scenario: Conflict detection - Healthcare Service already exists
    Given a 'Service' exists called 'TestGPPracticeConflictHCS' in DoS with attributes:
      | key                 | value                         |
      | id                  | 400005                        |
      | uid                 | 400005                        |
      | name                | TestGPPracticeConflictHCS     |
      | publicname          | Surgery for HCS Conflict Test |
      | typeid              | 100                           |
      | statusid            | 1                             |
      | odscode             | A12353                        |
      | createdtime         | 2024-01-01 10:00:00           |
      | modifiedtime        | 2024-01-01 10:00:00           |
      | openallhours        | false                         |
      | restricttoreferrals | false                         |
      | postcode            | SW1A 6FF                      |
      | address             | Buckingham Palace Road        |
      | town                | London                        |
      | web                 | https://www.nhs.uk/           |
      | email               | test6@nhs.net                 |
      | publicphone         | 0300 311 22 88                |
    When a record does not exist in the state table for key 'services#400005'
    And a record exists in the Healthcare Service table matching the transformed healthcare service ID for service 400005
    And a single service migration is run for ID '400005'
    Then the pipeline treats the record as an 'insert' operation
    And the DynamoDB TransactWriteItems request is rejected due to ConditionalCheckFailed
    And the pipeline logs "DynamoDB Transaction Cancelled - one or more items failed to write"
    And the migration records an error for service ID 400005

  @detect-changes @no-changes
  Scenario: No changes detected in organisation or endpoints
    Given a 'Service' exists called 'TestGPPracticeNoChanges' in DoS with attributes:
      | key                 | value                          |
      | id                  | 400006                         |
      | uid                 | 400006                         |
      | name                | TestGPPracticeNoChanges        |
      | publicname          | Surgery for No Changes Test    |
      | typeid              | 100                            |
      | statusid            | 1                              |
      | odscode             | A12354                         |
      | createdtime         | 2024-01-01 10:00:00            |
      | modifiedtime        | 2024-01-01 10:00:00            |
      | openallhours        | false                          |
      | restricttoreferrals | false                          |
      | postcode            | SW1A 7GG                       |
      | address             | Victoria Street                |
      | town                | London                         |
      | web                 | https://www.nhs.uk/            |
      | email               | test7@nhs.net                  |
      | publicphone         | 0300 311 22 99                 |
    When a single service migration is run for ID '400006'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#400006' with version 1
    When a single service migration is run for ID '400006'
    Then the pipeline treats the record as an 'update' operation
    And the pipeline logs "Skipping organisation update as no fields have changed since last migration"
    And no differences are found
    And the metrics should show 0 inserted, 0 updated records for the second run

  @detect-changes @organisation-name-change-dos
  Scenario: Organisation name changed from DoS update
    Given a 'Service' exists called 'TestGPPracticeOrgNameDos' in DoS with attributes:
      | key                 | value                            |
      | id                  | 400007                           |
      | uid                 | 400007                           |
      | name                | TestGPPracticeOrgNameDos         |
      | publicname          | Original Surgery Name            |
      | typeid              | 100                              |
      | statusid            | 1                                |
      | odscode             | A12355                           |
      | createdtime         | 2024-01-01 10:00:00              |
      | modifiedtime        | 2024-01-01 10:00:00              |
      | openallhours        | false                            |
      | restricttoreferrals | false                            |
      | postcode            | SW1A 8HH                         |
      | address             | Parliament Street                |
      | town                | London                           |
      | web                 | https://www.nhs.uk/              |
      | email               | test8@nhs.net                    |
      | publicphone         | 0300 311 33 00                   |
    When a single service migration is run for ID '400007'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#400007' with version 1
    When the service 'TestGPPracticeOrgNameDos' has its 'publicname' updated to 'Updated Surgery Name from DoS'
    And a single service migration is run for ID '400007'
    Then the pipeline treats the record as an 'update' operation
    And the pipeline logs "Organisation update detected, adding update item to transaction"
    And a difference is found in the organisation record
    And the metrics should show 0 inserted, 0 updated records for the second run

  @detect-changes @organisation-name-change-ods
  Scenario: Organisation name changed but was last updated from ODS
    Given a 'Service' exists called 'TestGPPracticeOrgNameOds' in DoS with attributes:
      | key                 | value                            |
      | id                  | 400008                           |
      | uid                 | 400008                           |
      | name                | TestGPPracticeOrgNameOds         |
      | publicname          | ODS Surgery Name                 |
      | typeid              | 100                              |
      | statusid            | 1                                |
      | odscode             | A12356                           |
      | createdtime         | 2024-01-01 10:00:00              |
      | modifiedtime        | 2024-01-01 10:00:00              |
      | openallhours        | false                            |
      | restricttoreferrals | false                            |
      | postcode            | SW1A 9JJ                         |
      | address             | Millbank                         |
      | town                | London                           |
      | web                 | https://www.nhs.uk/              |
      | email               | test9@nhs.net                    |
      | publicphone         | 0300 311 33 11                   |
    When a single service migration is run for ID '400008'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#400008' with version 1
    When the organisation for service '400008' is marked as last updated from ODS
    And the service 'TestGPPracticeOrgNameOds' has its 'publicname' updated to 'Changed Surgery Name'
    And a single service migration is run for ID '400008'
    Then the pipeline treats the record as an 'update' operation
    And the pipeline logs "Skipping organisation update as no fields have changed since last migration"
    And no differences are found
    And the metrics should show 0 inserted, 0 updated records for the second run

  @detect-changes @endpoint-change
  Scenario: Endpoint details changed
    Given a 'Service' exists called 'TestGPPracticeEndpointChange' in DoS with attributes:
      | key                 | value                              |
      | id                  | 400009                             |
      | uid                 | 400009                             |
      | name                | TestGPPracticeEndpointChange       |
      | publicname          | Surgery for Endpoint Test          |
      | typeid              | 100                                |
      | statusid            | 1                                  |
      | odscode             | A12357                             |
      | createdtime         | 2024-01-01 10:00:00                |
      | modifiedtime        | 2024-01-01 10:00:00                |
      | openallhours        | false                              |
      | restricttoreferrals | false                              |
      | postcode            | SW1A 0AA                           |
      | address             | Horse Guards Road                  |
      | town                | London                             |
      | web                 | https://www.original-website.uk/   |
      | email               | original@nhs.net                   |
      | publicphone         | 0300 311 33 22                     |
    When a single service migration is run for ID '400009'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#400009' with version 1
    When the service 'TestGPPracticeEndpointChange' has its 'web' updated to 'https://www.updated-website.uk/'
    And the service 'TestGPPracticeEndpointChange' has its 'email' updated to 'updated@nhs.net'
    And a single service migration is run for ID '400009'
    Then the pipeline treats the record as an 'update' operation
    And the pipeline logs "Healthcare service update detected, adding update item to transaction"
    And a difference is found in the endpoint record
    And the metrics should show 0 inserted, 0 updated records for the second run

  @detect-changes @multiple-changes
  Scenario: Both organisation name and endpoints changed
    Given a 'Service' exists called 'TestGPPracticeMultiChange' in DoS with attributes:
      | key                 | value                             |
      | id                  | 400010                            |
      | uid                 | 400010                            |
      | name                | TestGPPracticeMultiChange         |
      | publicname          | Surgery for Multiple Changes Test |
      | typeid              | 100                               |
      | statusid            | 1                                 |
      | odscode             | A12358                            |
      | createdtime         | 2024-01-01 10:00:00               |
      | modifiedtime        | 2024-01-01 10:00:00               |
      | openallhours        | false                             |
      | restricttoreferrals | false                             |
      | postcode            | SW1A 1BB                          |
      | address             | Great George Street               |
      | town                | London                            |
      | web                 | https://www.original.uk/          |
      | email               | original2@nhs.net                 |
      | publicphone         | 0300 311 33 33                    |
    When a single service migration is run for ID '400010'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#400010' with version 1
    When the service 'TestGPPracticeMultiChange' has its 'publicname' updated to 'Completely New Surgery Name'
    And the service 'TestGPPracticeMultiChange' has its 'web' updated to 'https://www.new-website.uk/'
    And the service 'TestGPPracticeMultiChange' has its 'email' updated to 'new@nhs.net'
    And a single service migration is run for ID '400010'
    Then the pipeline treats the record as an 'update' operation
    And the pipeline logs "Organisation update detected, adding update item to transaction"
    And the pipeline logs "Healthcare service update detected, adding update item to transaction"
    And a difference is found in the organisation record
    And a difference is found in the endpoint record
    And the metrics should show 0 inserted, 0 updated records for the second run
