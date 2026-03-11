@data-migration @status-field-updates
Feature: Organisation Active Status Updates
  Tests for organisation active field updates based on service status changes

  Validates the following scenarios:
  1. A new active service creates an active organisation.
  2. A new inactive service without an existing state record is skipped.
  3. An existing active organisation is updated to inactive when the service becomes inactive.
  4. An existing inactive organisation is updated to active when the service becomes active.

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: A new active service creates an active organisation.
    Given a "Service" exists in DoS with attributes
      | key                 | value                     |
      | id                  | 570001                    |
      | uid                 | 570001                    |
      | name                | Active Service Practice   |
      | odscode             | A57001                    |
      | openallhours        | FALSE                     |
      | restricttoreferrals | FALSE                     |
      | address             | 1 Active Street           |
      | town                | ACTIVETOWN                |
      | postcode            | AC1 1AA                   |
      | publicphone         | 01234 570001              |
      | email               | active1@nhs.net           |
      | web                 | www.active1.com           |
      | createdtime         | 2024-01-01 08:00:00.000   |
      | modifiedtime        | 2024-01-01 08:00:00.000   |
      | typeid              | 100                       |
      | statusid            | 1                         |
      | publicname          | Active Service Practice   |
      | latitude            | 51.5074                   |
      | longitude           | -0.1278                   |

    When the data migration process is run for table 'services', ID '570001' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570001' with version 1
    Then field 'active' on table 'organisation' for service ID '570001' has content:
      """
      {
        "active": true
      }
      """

  Scenario: A new inactive service without an existing state record is skipped.
    Given a "Service" exists in DoS with attributes
      | key                 | value                       |
      | id                  | 570002                      |
      | uid                 | 570002                      |
      | name                | Inactive Service Practice   |
      | odscode             | A57002                      |
      | openallhours        | FALSE                       |
      | restricttoreferrals | FALSE                       |
      | address             | 2 Inactive Street           |
      | town                | INACTIVETOWN                |
      | postcode            | IN2 2AA                     |
      | publicphone         | 01234 570002                |
      | email               | inactive2@nhs.net           |
      | web                 | www.inactive2.com           |
      | createdtime         | 2024-01-01 08:00:00.000     |
      | modifiedtime        | 2024-01-01 08:00:00.000     |
      | typeid              | 100                         |
      | statusid            | 2                           |
      | publicname          | Inactive Service Practice   |
      | latitude            | 51.5074                     |
      | longitude           | -0.1278                     |

    When the data migration process is run for table 'services', ID '570002' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 0 transformed, 0 inserted, 0 updated, 1 skipped and 0 errors
    And the state table does not contain a record for key 'services#570002'
    And no organisation was created for service '570002'

  Scenario: An existing active organisation is updated to inactive when the service becomes inactive.
    Given a "Service" exists in DoS with attributes
      | key                 | value                          |
      | id                  | 570003                         |
      | uid                 | 570003                         |
      | name                | Active to Inactive Practice    |
      | odscode             | A57003                         |
      | openallhours        | FALSE                          |
      | restricttoreferrals | FALSE                          |
      | address             | 3 Change Street                |
      | town                | CHANGETOWN                     |
      | postcode            | CH3 3AA                        |
      | publicphone         | 01234 570003                   |
      | email               | change3@nhs.net                |
      | web                 | www.change3.com                |
      | createdtime         | 2024-01-01 08:00:00.000        |
      | modifiedtime        | 2024-01-01 08:00:00.000        |
      | typeid              | 100                            |
      | statusid            | 1                              |
      | publicname          | Active to Inactive Practice    |
      | latitude            | 51.5074                        |
      | longitude           | -0.1278                        |

    When the data migration process is run for table 'services', ID '570003' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570003' with version 1
    Then field 'active' on table 'organisation' for service ID '570003' has content:
      """
      {
        "active": true
      }
      """

    # Update service to inactive status
    Given the "Service" with id "570003" is updated with attributes
      | key      | value |
      | statusid | 2     |

    When the data migration process is run for table 'services', ID '570003' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570003' with version 2
    Then field 'active' on table 'organisation' for service ID '570003' has content:
      """
      {
        "active": false
      }
      """

  Scenario: An existing organisation is set to inactive and then back to active as the service status changes.
    Given a "Service" exists in DoS with attributes
      | key                 | value                          |
      | id                  | 570004                         |
      | uid                 | 570004                         |
      | name                | Inactive to Active Practice    |
      | odscode             | A57004                         |
      | openallhours        | FALSE                          |
      | restricttoreferrals | FALSE                          |
      | address             | 4 Reactivate Street            |
      | town                | REACTIVETOWN                   |
      | postcode            | RE4 4AA                        |
      | publicphone         | 01234 570004                   |
      | email               | reactivate4@nhs.net            |
      | web                 | www.reactivate4.com            |
      | createdtime         | 2024-01-01 08:00:00.000        |
      | modifiedtime        | 2024-01-01 08:00:00.000        |
      | typeid              | 100                            |
      | statusid            | 1                              |
      | publicname          | Inactive to Active Practice    |
      | latitude            | 51.5074                        |
      | longitude           | -0.1278                        |

    When the data migration process is run for table 'services', ID '570004' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570004' with version 1
    Then field 'active' on table 'organisation' for service ID '570004' has content:
      """
      {
        "active": true
      }
      """

    # Update service to inactive status
    Given the "Service" with id "570004" is updated with attributes
      | key      | value |
      | statusid | 2     |

    When the data migration process is run for table 'services', ID '570004' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570004' with version 2
    Then field 'active' on table 'organisation' for service ID '570004' has content:
      """
      {
        "active": false
      }
      """

    # Reactivate the service
    Given the "Service" with id "570004" is updated with attributes
      | key      | value |
      | statusid | 1     |

    When the data migration process is run for table 'services', ID '570004' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#570004' with version 3
    Then field 'active' on table 'organisation' for service ID '570004' has content:
      """
      {
        "active": true
      }
      """
