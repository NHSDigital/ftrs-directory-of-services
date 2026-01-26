@data-migration @incremental-update
Feature: Incremental Updates - State Management and Validation

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

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
    And the state table contains a record for key 'services#570001' with version 2

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

    And the state table record for key 'services#570002' contains organisation ID
    And the state table record for key 'services#570002' contains location ID
    And the state table record for key 'services#570002' contains healthcare_service ID

    Given the "Service" with id "570002" is updated with attributes
      | key  | value                          |
      | name | State Check Practice - Updated |

    When the data migration process is run for table 'services', ID '570002' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570002' with version 2

  Scenario: Update service name field propagates to DynamoDB correctly
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

    Given the "Service" with id "570003" is updated with attributes
      | key  | value                                 |
      | name | Valid Reference Practice - Updated    |

    When the data migration process is run for table 'services', ID '570003' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570003' with version 2

  Scenario: Update with maximum field length is handled correctly
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570004                  |
      | uid                 | 570004                  |
      | name                | Boundary Test Practice  |
      | odscode             | V57004                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 8 Version Street        |
      | town                | VERSIONTOWN             |
      | postcode            | VS8 8AA                 |
      | publicphone         | 01234 570004            |
      | email               | boundary@nhs.net        |
      | web                 | www.boundary.com        |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Boundary Test Practice  |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '570004' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570004' with version 1

    Given the "Service" with id "570004" is updated with attributes
      | key  | value                                                                                           |
      | name | This is a long service name that tests field length handling in the incremental update process |

    When the data migration process is run for table 'services', ID '570004' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570004' with version 2

  Scenario: Update with high precision GPS coordinates preserves precision
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 570005                  |
      | uid                 | 570005                  |
      | name                | GPS Precision Practice  |
      | odscode             | V57005                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 9 Version Street        |
      | town                | VERSIONTOWN             |
      | postcode            | VS9 9AA                 |
      | publicphone         | 01234 570005            |
      | email               | gpsprecision@nhs.net    |
      | web                 | www.gpsprecision.com    |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | GPS Precision Practice  |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '570005' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570005' with version 1

    # Update coordinates with high precision (15 decimal places)
    Given the "Service" with id "570005" is updated with attributes
      | key       | value                |
      | latitude  | 51.123456789012345   |
      | longitude | -2.987654321098765   |

    When the data migration process is run for table 'services', ID '570005' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570005' with version 2
