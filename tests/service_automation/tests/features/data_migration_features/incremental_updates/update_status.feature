@data-migration @incremental-update
Feature: Incremental Updates - Service Status Changes
  Tests for updates involving service status transitions

  # NOTE: The GP Practice transformer only processes services with statusid=1 (active).
  # Services with other status values (commissioned=2, deleted=3, etc.) are SKIPPED
  # by the should_include_service check in the transformer.

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Update service status from active to inactive causes skip
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 560001                  |
      | uid                 | 560001                  |
      | name                | Status Change Practice  |
      | odscode             | F56001                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 1 Status Street         |
      | town                | STATUSTOWN              |
      | postcode            | ST1 1AA                 |
      | publicphone         | 01234 560001            |
      | email               | status1@nhs.net         |
      | web                 | www.status1.com         |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Status Change Practice  |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '560001' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#560001' with version 1

    # Change status to inactive/deleted (statusid=3) - service will be skipped
    Given the "Service" with id "560001" is updated with attributes
      | key      | value |
      | statusid | 3     |

    When the data migration process is run for table 'services', ID '560001' and method 'update'
    # Service with inactive status should be skipped during update
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 0 transformed, 0 inserted, 0 updated, 1 skipped and 0 errors

  Scenario: Update service status from active to commissioned causes skip
    Given a "Service" exists in DoS with attributes
      | key                 | value                        |
      | id                  | 560002                       |
      | uid                 | 560002                       |
      | name                | Commissioned Status Practice |
      | odscode             | F56002                       |
      | openallhours        | FALSE                        |
      | restricttoreferrals | FALSE                        |
      | address             | 2 Status Street              |
      | town                | STATUSTOWN                   |
      | postcode            | ST1 2AA                      |
      | publicphone         | 01234 560002                 |
      | email               | status2@nhs.net              |
      | web                 | www.status2.com              |
      | createdtime         | 2024-01-01 08:00:00.000      |
      | modifiedtime        | 2024-01-01 08:00:00.000      |
      | typeid              | 100                          |
      | statusid            | 1                            |
      | publicname          | Commissioned Status Practice |
      | latitude            | 51.5074                      |
      | longitude           | -0.1278                      |

    When the data migration process is run for table 'services', ID '560002' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#560002' with version 1

    # Change status to commissioned (statusid=2) - service will be skipped
    Given the "Service" with id "560002" is updated with attributes
      | key      | value |
      | statusid | 2     |

    When the data migration process is run for table 'services', ID '560002' and method 'update'
    # Commissioned status causes the service to be skipped (only active services are processed)
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 0 transformed, 0 inserted, 0 updated, 1 skipped and 0 errors

  Scenario: Update active service with other field changes
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 560003                      |
      | uid                 | 560003                      |
      | name                | Multi Field Status Practice |
      | odscode             | F56003                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 3 Status Street             |
      | town                | STATUSTOWN                  |
      | postcode            | ST1 3AA                     |
      | publicphone         | 01234 560003                |
      | email               | status3@nhs.net             |
      | web                 | www.status3.com             |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Multi Field Status Practice |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '560003' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#560003' with version 1

    # Keep status active and change other fields
    Given the "Service" with id "560003" is updated with attributes
      | key        | value               |
      | publicname | Updated Status Name |
      | email      | newstatus@nhs.net   |

    When the data migration process is run for table 'services', ID '560003' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#560003' with version 2
