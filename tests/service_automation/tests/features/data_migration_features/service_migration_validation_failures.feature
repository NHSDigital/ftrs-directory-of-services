@data-migration
Feature: Service Migration - Validation Failures
  As a test author
  I want to verify that services with missing required fields or invalid data are properly rejected
  So that I can confirm the migration process validates data integrity and prevents incomplete records from being created

  Scenario Outline: Services with missing required fields are rejected
    Given a 'Service' exists called '<service_name>' in DoS with attributes:
      | key                 | value                   |
      | id                  | <service_id>            |
      | uid                 | <uid>                   |
      | name                | <name>                  |
      | publicname          | <public_name>           |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | odscode             | <ods_code>              |
      | createdtime         | 2024-01-01 10:00:00     |
      | modifiedtime        | 2024-01-01 10:00:00     |
      | publicphone         | 0123456789              |
      | email               | test@nhs.net            |
      | web                 | https://www.test.nhs.uk |
      | postcode            | AB12 3CD                |
      | address             | 123 Test Street         |
      | town                | TestTown                |
      | openallhours        | false                   |
      | restricttoreferrals | false                   |
    When the service migration process is run for table 'services', ID '<service_id>' and method 'insert'
    Then the metrics should be 1 total, <expected_supported> supported, <expected_unsupported> unsupported, <expected_transformed> transformed, 0 inserted, 0 updated, 0 skipped, <expected_invalid> invalid and <expected_errors> errored
    And no organisation was created for service '<service_id>'
    And no location was created for service '<service_id>'
    And no healthcare service was created for service '<service_id>'

    Examples:
      | service_id | uid    | service_name          | name                   | public_name  | ods_code | expected_supported | expected_unsupported | expected_transformed | expected_invalid | expected_errors |
      | 400001     | 400001 | MissingPublicName     | GP: Missing PublicName |              | Y12345   | 1                  | 0                    | 0                    | 1                | 0               |
      | 400002     | 400002 | MissingODSCode        | GP: Missing ODS Code   | Test Surgery |          | 0                  | 1                    | 0                    | 0                | 0               |
      | 400003     | 400003 | MissingMultipleFields | GP: Multiple Missing   |              |          | 0                  | 1                    | 0                    | 0                | 0               |

  Scenario Outline: Services with invalid ODS code format are rejected
    Given a 'Service' exists called '<service_name>' in DoS with attributes:
      | key                 | value                      |
      | id                  | <service_id>               |
      | uid                 | <uid>                      |
      | name                | GP: Invalid ODS Code Test  |
      | publicname          | Invalid ODS Code Surgery   |
      | typeid              | 100                        |
      | statusid            | 1                          |
      | odscode             | <ods_code>                 |
      | createdtime         | 2024-01-01 10:00:00        |
      | modifiedtime        | 2024-01-01 10:00:00        |
      | publicphone         | 0123456789                 |
      | email               | invalid.ods@nhs.net        |
      | web                 | https://www.invalid-ods.uk |
      | postcode            | AB12 3CD                   |
      | address             | 123 Test Street            |
      | town                | TestTown                   |
      | openallhours        | false                      |
      | restricttoreferrals | false                      |
    When the service migration process is run for table 'services', ID '<service_id>' and method 'insert'
    Then the metrics should be 1 total, 0 supported, 1 unsupported, 0 transformed, 0 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And no organisation was created for service '<service_id>'
    And no location was created for service '<service_id>'
    And no healthcare service was created for service '<service_id>'

    Examples:
      | service_id | uid    | service_name    | ods_code        |
      | 400010     | 400010 | ODSTooShort     | ABC             |
      | 400011     | 400011 | ODSTooLong      | Y12345678901234 |
      | 400012     | 400012 | ODSSpecialChars | Y123-45         |
      | 400013     | 400013 | ODSWithSpaces   | Y12 345         |

  Scenario: Unsupported operation method is not processed
    Given a 'Service' exists called 'DeleteOperation' in DoS with attributes:
      | key                 | value                         |
      | id                  | 400020                        |
      | uid                 | 400020                        |
      | name                | GP: DELETE Test               |
      | publicname          | DELETE Operation Test         |
      | typeid              | 100                           |
      | statusid            | 1                             |
      | odscode             | Y12399                        |
      | createdtime         | 2024-01-01 10:00:00           |
      | modifiedtime        | 2024-01-01 10:00:00           |
      | publicphone         | 0123456789                    |
      | email               | operation.test@nhs.net        |
      | web                 | https://www.operation-test.uk |
      | postcode            | AB12 3CD                      |
      | address             | 123 Test Street               |
      | town                | TestTown                      |
      | openallhours        | false                         |
      | restricttoreferrals | false                         |
    When the service migration process is run for table 'services', ID '400020' and method 'delete'
    Then the metrics should be 0 total, 0 supported, 0 unsupported, 0 transformed, 0 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And no organisation was created for service '400020'
    And no location was created for service '400020'
    And no healthcare service was created for service '400020'

  Scenario: Service with incorrect service type is unsupported
    Given a 'Service' exists called 'WrongTypeService' in DoS with attributes:
      | key                 | value                    |
      | id                  | 400030                   |
      | uid                 | 400030                   |
      | name                | WrongTypeService         |
      | publicname          | Test Service             |
      | typeid              | 12                       |
      | statusid            | 1                        |
      | odscode             | Y12400                   |
      | createdtime         | 2024-01-01 10:00:00      |
      | modifiedtime        | 2024-01-01 10:00:00      |
      | publicphone         | 0123456789               |
      | email               | wrongtype@nhs.net        |
      | web                 | https://www.wrongtype.uk |
      | postcode            | AB12 3CD                 |
      | address             | 123 Test Street          |
      | town                | TestTown                 |
      | openallhours        | false                    |
      | restricttoreferrals | false                    |
    When the service migration process is run for table 'services', ID '400030' and method 'insert'
    Then the metrics should be 1 total, 0 supported, 1 unsupported, 0 transformed, 0 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And no organisation was created for service '400030'
    And no location was created for service '400030'
    And no healthcare service was created for service '400030'

  Scenario Outline: Services with inactive status are not included
    Given a 'Service' exists called '<service_name>' in DoS with attributes:
      | key                 | value                   |
      | id                  | <service_id>            |
      | uid                 | <uid>                   |
      | name                | <service_name>          |
      | publicname          | Inactive Test Service   |
      | typeid              | 100                     |
      | statusid            | <status_id>             |
      | odscode             | Y12410                  |
      | createdtime         | 2024-01-01 10:00:00     |
      | modifiedtime        | 2024-01-01 10:00:00     |
      | publicphone         | 0123456789              |
      | email               | inactive@nhs.net        |
      | web                 | https://www.inactive.uk |
      | postcode            | AB12 3CD                |
      | address             | 123 Test Street         |
      | town                | TestTown                |
      | openallhours        | false                   |
      | restricttoreferrals | false                   |
    When the service migration process is run for table 'services', ID '<service_id>' and method 'insert'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 0 transformed, 0 inserted, 0 updated, 1 skipped, 0 invalid and 0 errored
    And no organisation was created for service '<service_id>'
    And no location was created for service '<service_id>'
    And no healthcare service was created for service '<service_id>'
    And service ID '<service_id>' was skipped due to reason 'Service is not active'

    Examples:
      | service_id | uid    | service_name          | status_id |
      | 400040     | 400040 | InactiveStatusClosed  | 2         |
      | 400041     | 400041 | InactiveStatusDeleted | 3         |
