@data-migration @incremental-update
Feature: Incremental Updates - Organisation Field Changes
  Tests for verifying incremental updates to Organisation entity fields

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Update organisation name via publicname change
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 500001                  |
      | uid                 | 500001                  |
      | name                | Original Practice Name  |
      | odscode             | A50001                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 1 Test Street           |
      | town                | TESTTOWN                |
      | postcode            | TE1 1AA                 |
      | publicphone         | 01234 111111            |
      | email               | test@nhs.net            |
      | web                 | www.test.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Original Practice Name  |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '500001' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#500001' with version 1
    Then field 'name' on table 'organisation' for id '3e15383d-504d-5247-abf9-2147a21da73b' has content:
      """
      {
        "name": "Original Practice Name"
      }
      """

    Given the "Service" with id "500001" is updated with attributes
      | key        | value                 |
      | publicname | Updated Practice Name |

    When the data migration process is run for table 'services', ID '500001' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#500001' with version 2
    Then field 'name' on table 'organisation' for id '3e15383d-504d-5247-abf9-2147a21da73b' has content:
      """
      {
        "name": "Updated Practice Name"
      }
      """

  Scenario: Update organisation ODS code - current functionality allows ODS code change if valid
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 500002                  |
      | uid                 | 500002                  |
      | name                | ODS Code Test Practice  |
      | odscode             | A50002                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 2 Test Street           |
      | town                | TESTTOWN                |
      | postcode            | TE1 2AA                 |
      | publicphone         | 01234 222222            |
      | email               | test2@nhs.net           |
      | web                 | www.test2.com           |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | ODS Code Test Practice  |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '500002' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#500002' with version 1
    And field 'identifier_ODS_ODSCode' on table 'organisation' for id '8d413995-5589-50f3-908f-73f63c302ad3' has content:
      """
      {
        "identifier_ODS_ODSCode": "A50002"
      }
      """

    Given the "Service" with id "500002" is updated with attributes
      | key     | value  |
      | odscode | A50003 |

    When the data migration process is run for table 'services', ID '500002' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#500002' with version 2
    And field 'identifier_ODS_ODSCode' on table 'organisation' for id '8d413995-5589-50f3-908f-73f63c302ad3' has content:
      """
      {
        "identifier_ODS_ODSCode": "A50003"
      }
      """

  Scenario: Update with no actual changes skips update
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 500003                  |
      | uid                 | 500003                  |
      | name                | No Change Practice      |
      | odscode             | A50004                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 3 Test Street           |
      | town                | TESTTOWN                |
      | postcode            | TE1 3AA                 |
      | publicphone         | 01234 333333            |
      | email               | test3@nhs.net           |
      | web                 | www.test3.com           |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | No Change Practice      |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '500003' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#500003' with version 1
    And the 'organisation' for service ID '500003' has content:
      """
      {
        "id": "4f86d49b-e8cf-5230-9c2f-d5951bddf786",
        "active": true,
        "createdBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "created": "2026-01-12T13:20:56.027889Z",
        "endpoints": [],
        "field": "document",
        "identifier_ODS_ODSCode": "A50004",
        "identifier_oldDoS_uid": "500003",
        "legalDates": null,
        "lastUpdatedBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "lastUpdated": "2026-01-12T13:20:56.027889Z",
        "name": "No Change Practice",
        "type": "GP Practice",
        "primary_role_code": null,
        "non_primary_role_codes": [],
        "telecom": []
      }
      """

    # Run update without changing any data
    When the data migration process is run for table 'services', ID '500003' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#500003' with version 1
    And the 'organisation' for service ID '500003' has content:
      """
      {
        "id": "4f86d49b-e8cf-5230-9c2f-d5951bddf786",
        "active": true,
        "createdBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "created": "2026-01-12T13:20:56.027889Z",
        "endpoints": [],
        "field": "document",
        "identifier_ODS_ODSCode": "A50004",
        "identifier_oldDoS_uid": "500003",
        "legalDates": null,
        "lastUpdatedBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "lastUpdated": "2026-01-12T13:20:56.027889Z",
        "name": "No Change Practice",
        "type": "GP Practice",
        "primary_role_code": null,
        "non_primary_role_codes": [],
        "telecom": []
      }
      """
