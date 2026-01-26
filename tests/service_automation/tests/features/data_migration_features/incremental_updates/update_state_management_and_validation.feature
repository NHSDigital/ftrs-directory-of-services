@data-migration @incremental-update @state-management @validation
Feature: Incremental Updates - State Management and Validation

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  @ready-to-run
  Scenario: Multiple field updates in single transaction update state version once
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 570001                      |
      | uid                 | 570001                      |
      | name                | Multi Field Practice        |
      | odscode             | V57001                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 2 Version Street            |
      | town                | VERSIONTOWN                 |
      | postcode            | VS2 2AA                     |
      | publicphone         | 01234 570001                |
      | email               | multifield@nhs.net          |
      | web                 | www.multifield.com          |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Multi Field Practice        |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '570001' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570001' with version 1

    # Update multiple fields at once
    Given the "Service" with id "570001" is updated with attributes
      | key         | value                            |
      | name        | Multi Field Practice - Updated   |
      | publicname  | Multi Field Practice - Updated   |
      | address     | 99 Changed Address               |
      | postcode    | CH9 9AA                          |
      | publicphone | 01234 888888                     |
      | email       | changed@nhs.net                  |
      | web         | www.changed.com                  |
      | latitude    | 52.1234                          |
      | longitude   | -1.5678                          |

    When the data migration process is run for table 'services', ID '570001' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    # Version should only increment by 1 despite multiple field changes
    And the state table contains a record for key 'services#570001' with version 2

  @missing-steps
  Scenario: Update when state table record exists validates correctly
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570002                  |
      | uid                 | 570002                  |
      | name                | State Check Practice    |
      | odscode             | V57002                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 3 Version Street        |
      | town                | VERSIONTOWN             |
      | postcode            | VS3 3AA                 |
      | publicphone         | 01234 570002            |
      | email               | statecheck@nhs.net      |
      | web                 | www.statecheck.com      |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | State Check Practice    |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '570002' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570002' with version 1

    # Verify state table has all 3 entity IDs stored
    And the state table record for key 'services#570002' contains organisation ID
    And the state table record for key 'services#570002' contains location ID
    And the state table record for key 'services#570002' contains healthcare_service ID

    # Update should use stored state to perform incremental update
    Given the "Service" with id "570002" is updated with attributes
      | key  | value                          |
      | name | State Check Practice - Updated |

    When the data migration process is run for table 'services', ID '570002' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570002' with version 2

  @missing-steps
  Scenario: Update HealthcareService with valid providedBy reference succeeds
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570003                  |
      | uid                 | 570003                  |
      | name                | Valid Reference Practice|
      | odscode             | V57003                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 4 Version Street        |
      | town                | VERSIONTOWN             |
      | postcode            | VS4 4AA                 |
      | publicphone         | 01234 570003            |
      | email               | validref@nhs.net        |
      | web                 | www.validref.com        |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Valid Reference Practice|
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '570003' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570003' with version 1

    # Verify providedBy reference exists and points to Organisation
    And the DynamoDB record for healthcare-service contains valid providedBy UUID
    And the referenced Organisation record exists in DynamoDB

    # Update should maintain valid reference
    Given the "Service" with id "570003" is updated with attributes
      | key  | value                                 |
      | name | Valid Reference Practice - Updated    |

    When the data migration process is run for table 'services', ID '570003' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the DynamoDB record for healthcare-service still contains same providedBy UUID

  @missing-steps
  Scenario: Update with invalid enum value is handled gracefully
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570004                  |
      | uid                 | 570004                  |
      | name                | Enum Test Practice      |
      | odscode             | V57004                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 5 Version Street        |
      | town                | VERSIONTOWN             |
      | postcode            | VS5 5AA                 |
      | publicphone         | 01234 570004            |
      | email               | enumtest@nhs.net        |
      | web                 | www.enumtest.com        |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Enum Test Practice      |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '570004' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570004' with version 1

    # Update with invalid statusid that doesn't map to valid enum
    Given the "Service" with id "570004" is updated with attributes
      | key      | value |
      | statusid | 9999  |

    When the data migration process is run for table 'services', ID '570004' and method 'update'
    # System should either skip (if validation catches it) or error (if not supported)
    # This validates error handling exists for invalid enum mappings
    Then the SQS event should be processed without causing system failure
    And appropriate error or skip should be recorded in metrics

  @missing-steps
  Scenario: Update with maximum field length is handled correctly
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570005                  |
      | uid                 | 570005                  |
      | name                | Boundary Test Practice  |
      | odscode             | V57005                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 8 Version Street        |
      | town                | VERSIONTOWN             |
      | postcode            | VS8 8AA                 |
      | publicphone         | 01234 570005            |
      | email               | boundary@nhs.net        |
      | web                 | www.boundary.com        |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Boundary Test Practice  |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '570005' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570005' with version 1

    # Update with very long name (test field length handling)
    Given the "Service" with id "570005" is updated with attributes
      | key  | value                                                                                                                                                                                                                                                                   |
      | name | This is an extremely long service name that tests the maximum field length handling in the incremental update process to ensure that long strings are properly processed and stored in DynamoDB without truncation or error and this name is exactly 255 chars long!!! |

    When the data migration process is run for table 'services', ID '570005' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570005' with version 2
    # Verify full name is stored (no truncation)
    And field 'name' on table 'healthcare-service' contains the full updated name

  @ready-to-run
  Scenario: Update with high precision GPS coordinates preserves precision
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570006                  |
      | uid                 | 570006                  |
      | name                | GPS Precision Practice  |
      | odscode             | V57006                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 9 Version Street        |
      | town                | VERSIONTOWN             |
      | postcode            | VS9 9AA                 |
      | publicphone         | 01234 570006            |
      | email               | gpsprecision@nhs.net    |
      | web                 | www.gpsprecision.com    |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | GPS Precision Practice  |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '570006' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570006' with version 1

    # Update coordinates with high precision (15 decimal places)
    Given the "Service" with id "570006" is updated with attributes
      | key       | value                |
      | latitude  | 51.123456789012345   |
      | longitude | -2.987654321098765   |

    When the data migration process is run for table 'services', ID '570006' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570006' with version 2
    # Verify precision is maintained (Decimal as string in DynamoDB)
    And field 'positionGCS' on table 'location' for id 'e2g7f0b6-9e5c-5dd4-e8f1-2g0b6c4d7e8f' has content:
      """
      {
        "positionGCS": {
          "latitude": "51.123456789012345",
          "longitude": "-2.987654321098765"
        }
      }
      """
