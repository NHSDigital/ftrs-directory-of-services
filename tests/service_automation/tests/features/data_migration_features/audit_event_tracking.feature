@data-migration @audit-events
Feature: Data Migration - Audit Event Tracking
  Track who created and modified records through data migration pipeline

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: INSERT operation - Audit fields populated on Organisation creation
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 700001                      |
      | uid                 | 700001                      |
      | name                | Audit Test Practice 1       |
      | odscode             | A70001                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 1 Audit Street              |
      | town                | AUDITTOWN                   |
      | postcode            | AU1 1AA                     |
      | publicphone         | 01234 700001                |
      | email               | audit1@nhs.net              |
      | web                 | www.audit1.com              |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Audit Test Practice 1       |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '700001' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the organisation record for healthcare service has "createdTime" populated
    And the organisation "createdBy.type" is "app"
    And the organisation "createdBy.value" is "INTERNAL001"
    And the organisation "createdBy.display" is "Data Migration"
    And the organisation "lastUpdated" equals "createdTime"
    And the organisation "lastUpdatedBy" equals "createdBy"

  Scenario: INSERT operation - Audit fields populated on Location creation
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 700002                      |
      | uid                 | 700002                      |
      | name                | Audit Test Practice 2       |
      | odscode             | A70002                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 2 Audit Street              |
      | town                | AUDITTOWN                   |
      | postcode            | AU2 2AA                     |
      | publicphone         | 01234 700002                |
      | email               | audit2@nhs.net              |
      | web                 | www.audit2.com              |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Audit Test Practice 2       |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '700002' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the location record has "createdTime" populated
    And the location "createdBy.type" is "app"
    And the location "createdBy.value" is "INTERNAL001"
    And the location "createdBy.display" is "Data Migration"
    And the location "lastUpdated" equals "createdTime"
    And the location "lastUpdatedBy" equals "createdBy"

  Scenario: INSERT operation - Audit fields populated on HealthcareService creation
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 700003                      |
      | uid                 | 700003                      |
      | name                | Audit Test Practice 3       |
      | odscode             | A70003                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 3 Audit Street              |
      | town                | AUDITTOWN                   |
      | postcode            | AU3 3AA                     |
      | publicphone         | 01234 700003                |
      | email               | audit3@nhs.net              |
      | web                 | www.audit3.com              |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Audit Test Practice 3       |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '700003' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the healthcare service record has "createdTime" populated
    And the healthcare service "createdBy.type" is "app"
    And the healthcare service "createdBy.value" is "INTERNAL001"
    And the healthcare service "createdBy.display" is "Data Migration"
    And the healthcare service "lastUpdated" equals "createdTime"
    And the healthcare service "lastUpdatedBy" equals "createdBy"

  Scenario: INSERT operation - Audit fields populated on Endpoint creation
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 700004                      |
      | uid                 | 700004                      |
      | name                | Audit Test Practice 4       |
      | odscode             | A70004                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 4 Audit Street              |
      | town                | AUDITTOWN                   |
      | postcode            | AU4 4AA                     |
      | publicphone         | 01234 700004                |
      | email               | audit4@nhs.net              |
      | web                 | www.audit4.com              |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Audit Test Practice 4       |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '700004' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the endpoint records have "createdTime" populated
    And all endpoints "createdBy.type" is "app"
    And all endpoints "createdBy.value" is "INTERNAL001"
    And all endpoints "createdBy.display" is "Data Migration"
    And all endpoints "lastUpdated" equals "createdTime"
    And all endpoints "lastUpdatedBy" equals "createdBy"

  Scenario: UPDATE operation - Audit fields updated on Organisation modification
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 700005                      |
      | uid                 | 700005                      |
      | name                | Audit Test Practice 5       |
      | odscode             | A70005                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 5 Audit Street              |
      | town                | AUDITTOWN                   |
      | postcode            | AU5 5AA                     |
      | publicphone         | 01234 700005                |
      | email               | audit5@nhs.net              |
      | web                 | www.audit5.com              |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Audit Test Practice 5       |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '700005' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors

    Given I store the organisation audit timestamps for service '700005'
    And the "Service" with id "700005" is updated with attributes
      | key        | value                           |
      | publicname | Audit Test Practice 5 - Updated |

    When the data migration process is run for table 'services', ID '700005' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the organisation "createdTime" is unchanged from stored value
    And the organisation "createdBy" is unchanged from stored value
    And the organisation "lastUpdated" is greater than stored "createdTime"
    And the organisation "lastUpdatedBy.type" is "app"
    And the organisation "lastUpdatedBy.value" is "INTERNAL001"
    And the organisation "lastUpdatedBy.display" is "Data Migration"

  Scenario: UPDATE operation - Audit fields updated on Location modification
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 700006                      |
      | uid                 | 700006                      |
      | name                | Audit Test Practice 6       |
      | odscode             | A70006                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 6 Audit Street              |
      | town                | AUDITTOWN                   |
      | postcode            | AU6 6AA                     |
      | publicphone         | 01234 700006                |
      | email               | audit6@nhs.net              |
      | web                 | www.audit6.com              |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Audit Test Practice 6       |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '700006' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors

    Given I store the location audit timestamps for service '700006'
    And the "Service" with id "700006" is updated with attributes
      | key      | value              |
      | address  | 99 Changed Address |
      | postcode | CH9 9AA            |

    When the data migration process is run for table 'services', ID '700006' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the location "createdTime" is unchanged from stored value
    And the location "createdBy" is unchanged from stored value
    And the location "lastUpdated" is greater than stored "createdTime"
    And the location "lastUpdatedBy.type" is "app"
    And the location "lastUpdatedBy.value" is "INTERNAL001"
    And the location "lastUpdatedBy.display" is "Data Migration"

  Scenario: UPDATE operation - Audit fields updated on HealthcareService modification
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 700007                      |
      | uid                 | 700007                      |
      | name                | Audit Test Practice 7       |
      | odscode             | A70007                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 7 Audit Street              |
      | town                | AUDITTOWN                   |
      | postcode            | AU7 7AA                     |
      | publicphone         | 01234 700007                |
      | email               | audit7@nhs.net              |
      | web                 | www.audit7.com              |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Audit Test Practice 7       |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '700007' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors

    Given I store the healthcare service audit timestamps for service '700007'
    And the "Service" with id "700007" is updated with attributes
      | key  | value                           |
      | name | Audit Test Practice 7 - Updated |

    When the data migration process is run for table 'services', ID '700007' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the healthcare service "createdTime" is unchanged from stored value
    And the healthcare service "createdBy" is unchanged from stored value
    And the healthcare service "lastUpdated" is greater than stored "createdTime"
    And the healthcare service "lastUpdatedBy.type" is "app"
    And the healthcare service "lastUpdatedBy.value" is "INTERNAL001"
    And the healthcare service "lastUpdatedBy.display" is "Data Migration"

  Scenario: UPDATE operation - Audit fields updated on Endpoint modification
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 700008                      |
      | uid                 | 700008                      |
      | name                | Audit Test Practice 8       |
      | odscode             | A70008                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 8 Audit Street              |
      | town                | AUDITTOWN                   |
      | postcode            | AU8 8AA                     |
      | publicphone         | 01234 700008                |
      | email               | audit8@nhs.net              |
      | web                 | www.audit8.com              |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 1                           |
      | publicname          | Audit Test Practice 8       |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '700008' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors

    Given I store the endpoint audit timestamps for service '700008'
    And the "Service" with id "700008" is updated with attributes
      | key   | value                   |
      | email | changed_email@nhs.net   |
      | web   | www.changed-audit8.com  |

    When the data migration process is run for table 'services', ID '700008' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And all endpoints "createdTime" is unchanged from stored value
    And all endpoints "createdBy" is unchanged from stored value
    And all endpoints "lastUpdated" is greater than stored "createdTime"
    And all endpoints "lastUpdatedBy.type" is "app"
    And all endpoints "lastUpdatedBy.value" is "INTERNAL001"
    And all endpoints "lastUpdatedBy.display" is "Data Migration"
