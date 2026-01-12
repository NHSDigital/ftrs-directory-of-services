@data-migration @incremental-update
Feature: Incremental Updates - Edge Cases and Special Scenarios
  Tests for edge cases in the incremental update functionality

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Update with no actual changes results in skip
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 530001                  |
      | uid                 | 530001                  |
      | name                | No Change Practice      |
      | odscode             | D53001                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 1 Unchanged Street      |
      | town                | UNCHANGEDTOWN           |
      | postcode            | NC1 1AA                 |
      | publicphone         | 01234 530001            |
      | email               | nochange@nhs.net        |
      | web                 | www.nochange.com        |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | No Change Practice      |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '530001' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530001' with version 1

    # Run update without changing any attributes - just modifiedtime
    Given the "Service" with id "530001" is updated with attributes
      | key          | value               |
      | modifiedtime | 2024-06-01 10:00:00 |

    When the data migration process is run for table 'services', ID '530001' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530001' with version 1

  Scenario: Add value to previously null email field
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 530002                  |
      | uid                 | 530002                  |
      | name                | Null To Value Practice  |
      | odscode             | D53002                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 2 Edge Case Street      |
      | town                | EDGETOWN                |
      | postcode            | ED2 2AA                 |
      | publicphone         | 01234 530002            |
      | email               |                         |
      | web                 |                         |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Null To Value Practice  |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '530002' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530002' with version 1
    And field 'telecom' on table 'healthcare-service' for id 'cb7b80c9-c215-550f-815b-6a7aa5cc66b7' has content:
      """
      {
        "telecom": {
          "email": null,
          "web": null,
          "phone_public": "01234530002",
          "phone_private": null
        }
      }
      """

    Given the "Service" with id "530002" is updated with attributes
      | key   | value              |
      | email | newlyadded@nhs.net |
      | web   | www.newlyadded.com |

    When the data migration process is run for table 'services', ID '530002' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530002' with version 2
    Then field 'telecom' on table 'healthcare-service' for id 'cb7b80c9-c215-550f-815b-6a7aa5cc66b7' has content:
      """
      {
        "telecom": {
          "email": "newlyadded@nhs.net",
          "web": "www.newlyadded.com",
          "phone_public": "01234530002",
          "phone_private": null
        }
      }
      """


  Scenario: Clear value by setting field to null/empty
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 530003                  |
      | uid                 | 530003                  |
      | name                | Value To Null Practice  |
      | odscode             | D53003                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 3 Edge Case Street      |
      | town                | EDGETOWN                |
      | postcode            | ED3 3AA                 |
      | publicphone         | 01234 530003            |
      | email               | tobecleared@nhs.net     |
      | web                 | www.tobecleared.com     |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Value To Null Practice  |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '530003' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530003' with version 1
    Then field 'telecom' on table 'healthcare-service' for id '89b99a3b-3644-5e74-bd50-0d501b9add18' has content:
      """
      {
        "telecom": {
          "email": "tobecleared@nhs.net",
          "web": "www.tobecleared.com",
          "phone_public": "01234530003",
          "phone_private": null
        }
      }
      """

    Given the "Service" with id "530003" is updated with attributes
      | key   | value |
      | email |       |
      | web   |       |

    When the data migration process is run for table 'services', ID '530003' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530003' with version 2
    Then field 'telecom' on table 'healthcare-service' for id '89b99a3b-3644-5e74-bd50-0d501b9add18' has content:
      """
      {
        "telecom": {
          "email": null,
          "web": null,
          "phone_public": "01234530003",
          "phone_private": null
        }
      }
      """

  Scenario: Multiple consecutive updates increment version correctly
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 530004                  |
      | uid                 | 530004                  |
      | name                | Multi Update Practice   |
      | odscode             | D53004                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 4 Edge Case Street      |
      | town                | EDGETOWN                |
      | postcode            | ED4 4AA                 |
      | publicphone         | 01234 530004            |
      | email               | multi1@nhs.net          |
      | web                 | www.multi1.com          |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Multi Update Practice   |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    # Initial insert - version 1
    When the data migration process is run for table 'services', ID '530004' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530004' with version 1

    # First update - version 2
    Given the "Service" with id "530004" is updated with attributes
      | key   | value          |
      | email | multi2@nhs.net |

    When the data migration process is run for table 'services', ID '530004' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530004' with version 2

    # Second update - version 3
    Given the "Service" with id "530004" is updated with attributes
      | key   | value          |
      | email | multi3@nhs.net |


    When the data migration process is run for table 'services', ID '530004' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530004' with version 3

    # Third update - version 4
    Given the "Service" with id "530004" is updated with attributes
      | key   | value          |
      | email | multi4@nhs.net |


    When the data migration process is run for table 'services', ID '530004' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530004' with version 4

  Scenario: Skipped update followed by actual update
    Given a "Service" exists in DoS with attributes
      | key                 | value                     |
      | id                  | 530005                    |
      | uid                 | 530005                    |
      | name                | Skip Then Update Practice |
      | odscode             | D53005                    |
      | openallhours        | FALSE                     |
      | restricttoreferrals | FALSE                     |
      | address             | 5 Edge Case Street        |
      | town                | EDGETOWN                  |
      | postcode            | ED5 5AA                   |
      | publicphone         | 01234 530005              |
      | email               | skip@nhs.net              |
      | web                 | www.skip.com              |
      | createdtime         | 2024-01-01 08:00:00.000   |
      | modifiedtime        | 2024-01-01 08:00:00.000   |
      | typeid              | 100                       |
      | statusid            | 1                         |
      | publicname          | Skip Then Update Practice |
      | latitude            | 51.5074                   |
      | longitude           | -0.1278                   |

    # Initial insert
    When the data migration process is run for table 'services', ID '530005' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530005' with version 1

    # No-op update - should skip, version stays at 1
    Given the "Service" with id "530005" is updated with attributes
      | key          | value               |
      | modifiedtime | 2024-06-01 10:00:00 |

    When the data migration process is run for table 'services', ID '530005' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530005' with version 1

    # Real update - should update, version becomes 2
    Given the "Service" with id "530005" is updated with attributes
      | key   | value           |
      | email | updated@nhs.net |


    When the data migration process is run for table 'services', ID '530005' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530005' with version 2

  Scenario: Update with special characters in organisation name
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 530006                  |
      | uid                 | 530006                  |
      | name                | Simple Practice Name    |
      | odscode             | D53006                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 6 Edge Case Street      |
      | town                | EDGETOWN                |
      | postcode            | ED6 6AA                 |
      | publicphone         | 01234 530006            |
      | email               | special@nhs.net         |
      | web                 | www.special.com         |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Simple Practice         |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '530006' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530006' with version 1
    And field 'name' on table 'organisation' for id '055cd0bf-02a1-5d82-a4c4-11685bedb9aa' has content:
      """
      {
        "name": "Simple Practice"
      }
      """

    Given the "Service" with id "530006" is updated with attributes
      | key        | value                        |
      | publicname | Dr Smith & Partners Practice |


    When the data migration process is run for table 'services', ID '530006' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530006' with version 2
    And field 'name' on table 'organisation' for id '055cd0bf-02a1-5d82-a4c4-11685bedb9aa' has content:
      """
      {
        "name": "Dr Smith & Partners Practice"
      }
      """


  Scenario: Update with very long values in fields
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 530007                  |
      | uid                 | 530007                  |
      | name                | Short Name              |
      | odscode             | D53007                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 7 Edge Case Street      |
      | town                | EDGETOWN                |
      | postcode            | ED7 7AA                 |
      | publicphone         | 01234 530007            |
      | email               | long@nhs.net            |
      | web                 | www.long.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Short Name              |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '530007' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530007' with version 1
    And field 'name' on table 'organisation' for id 'd3781fa9-2fdb-5e4d-883a-7b26f0c57acd' has content:
      """
      {
        "name": "Short Name"
      }
      """
    And field 'address' on table 'location' for id 'c4804c7a-9d0b-5133-a05c-b84f153d065d' has content:
      """
      {
        "address": {
          "line1": "7 Edge Case Street",
          "line2": null,
          "county": null,
          "town": "EDGETOWN",
          "postcode": "ED7 7AA"
        }
      }
      """

    Given the "Service" with id "530007" is updated with attributes
      | key        | value                                                                                                                     |
      | publicname | This Is A Very Long Practice Name That Might Test Our Systems Ability To Handle Long Strings In The Update Process        |
      | address    | Unit 123A Floor 45 Building Block C The Very Long Named Medical Complex Healthcare Campus Industrial Estate Business Park |

    When the data migration process is run for table 'services', ID '530007' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#530007' with version 2
    And field 'name' on table 'organisation' for id 'd3781fa9-2fdb-5e4d-883a-7b26f0c57acd' has content:
      """
      {
        "name": "This Is A Very Long Practice Name That Might Test Our Systems Ability To Handle Long Strings In The Update Process"
      }
      """
    And field 'address' on table 'location' for id 'c4804c7a-9d0b-5133-a05c-b84f153d065d' has content:
      """
      {
        "address": {
          "line1": "Unit 123A Floor 45 Building Block C The Very Long Named Medical Complex Healthcare Campus Industrial Estate Business Park",
          "line2": null,
          "county": null,
          "town": "EDGETOWN",
          "postcode": "ED7 7AA"
        }
      }
      """
