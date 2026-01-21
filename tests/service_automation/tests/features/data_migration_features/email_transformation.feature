@data-migration
Feature: Email Transformation

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario Outline: Valid email addresses are transformed correctly
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                             |
      | id                                  | <service_id>                                      |
      | uid                                 | <uid>                                             |
      | name                                | GP: <description>                                 |
      | odscode                             | <odscode>                                         |
      | isnational                          |                                                   |
      | openallhours                        | false                                             |
      | publicreferralinstructions          |                                                   |
      | telephonetriagereferralinstructions | Email test referral instructions                  |
      | restricttoreferrals                 | true                                              |
      | address                             | Test Surgery$10 Test Street$Test City$Test County |
      | town                                | TEST CITY                                         |
      | postcode                            | TE1 1ST                                           |
      | easting                             | 400000                                            |
      | northing                            | 500000                                            |
      | publicphone                         | 01234567890                                       |
      | nonpublicphone                      | 01234567891                                       |
      | fax                                 | 01234567892                                       |
      | email                               | <email>                                           |
      | web                                 | https://www.test.co.uk/                           |
      | createdby                           | HUMAN                                             |
      | createdtime                         | 2020-01-01 10:00:00.000                           |
      | modifiedby                          | ROBOT                                             |
      | modifiedtime                        | 2024-01-01 10:00:00.000                           |
      | lasttemplatename                    | Test Template                                     |
      | lasttemplateid                      | 100001                                            |
      | typeid                              | 100                                               |
      | parentid                            | 1527                                              |
      | subregionid                         | 1527                                              |
      | statusid                            | 1                                                 |
      | organisationid                      |                                                   |
      | returnifopenminutes                 |                                                   |
      | publicname                          | <description>                                     |
      | latitude                            | 51.5074                                           |
      | longitude                           | -0.1278                                           |
      | professionalreferralinfo            |                                                   |
      | lastverified                        |                                                   |
      | nextverificationdue                 |                                                   |

    When the data migration process is run for table 'services', ID '<service_id>' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then the state table contains a record for key 'services#<service_id>' with version 1
    Then the state table contains 0 validation issue(s) for key 'services#<service_id>'
    Then field 'telecom' on table 'healthcare-service' for id '<uuid>' has content:
      """
      {
        "telecom": {
          "email": "<email>",
          "phone_private": "01234567891",
          "phone_public": "01234567890",
          "web": "https://www.test.co.uk/"
        }
      }
      """

    Examples:
      | service_id | uid    | odscode | description              | email                           | uuid                                 |
      | 2101001    | 210001 | A23456  | Valid Email              | valid.email@nhs.net             | a16169ab-004c-5b51-803f-a621a064bfa2 |
      | 2101002    | 210002 | A23457  | Email with Special Chars | user.name+tag@subdomain.nhs.net | 3e2aaff1-cd62-5fa7-b3bf-c402f33bb316 |


  Scenario Outline: Invalid email addresses trigger validation issues
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                             |
      | id                                  | <service_id>                                      |
      | uid                                 | <uid>                                             |
      | name                                | GP: <description>                                 |
      | odscode                             | <odscode>                                         |
      | isnational                          |                                                   |
      | openallhours                        | false                                             |
      | publicreferralinstructions          |                                                   |
      | telephonetriagereferralinstructions | Email test referral instructions                  |
      | restricttoreferrals                 | true                                              |
      | address                             | Test Surgery$10 Test Street$Test City$Test County |
      | town                                | TEST CITY                                         |
      | postcode                            | TE1 1ST                                           |
      | easting                             | 400000                                            |
      | northing                            | 500000                                            |
      | publicphone                         | 01234567890                                       |
      | nonpublicphone                      | 01234567891                                       |
      | fax                                 | 01234567892                                       |
      | email                               | <email>                                           |
      | web                                 | https://www.test.co.uk/                           |
      | createdby                           | HUMAN                                             |
      | createdtime                         | 2020-01-01 10:00:00.000                           |
      | modifiedby                          | ROBOT                                             |
      | modifiedtime                        | 2024-01-01 10:00:00.000                           |
      | lasttemplatename                    | Test Template                                     |
      | lasttemplateid                      | 100001                                            |
      | typeid                              | 100                                               |
      | parentid                            | 1527                                              |
      | subregionid                         | 1527                                              |
      | statusid                            | 1                                                 |
      | organisationid                      |                                                   |
      | returnifopenminutes                 |                                                   |
      | publicname                          | <description>                                     |
      | latitude                            | 51.5074                                           |
      | longitude                           | -0.1278                                           |
      | professionalreferralinfo            |                                                   |
      | lastverified                        |                                                   |
      | nextverificationdue                 |                                                   |

    When the data migration process is run for table 'services', ID '<service_id>' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then the state table contains a record for key 'services#<service_id>' with version 1
    Then the state table contains 1 validation issue(s) for key 'services#<service_id>'
    Then the state table contains the following validation issues for key 'services#<service_id>':
      | expression | code                  | severity | diagnostics            | value   |
      | email      | <expected_error_code> | error    | <expected_diagnostics> | <email> |

    Then field 'telecom' on table 'healthcare-service' for id '<uuid>' has content:
      """
      {
        "telecom": {
          "email": null,
          "phone_private": "01234567891",
          "phone_public": "01234567890",
          "web": "https://www.test.co.uk/"
        }
      }
      """

    Examples:
      | service_id | uid    | odscode | description       | email             | uuid                                 | expected_error_code | expected_diagnostics     |
      | 2102001    | 210201 | B23456  | Empty Email       |                   | f0e0264a-7cbd-5f1e-afda-ccc02da9aea3 | email_not_string    | Email must be a string   |
      | 2102002    | 210202 | B23457  | Invalid Format    | invalidemail      | 275eea01-a750-5b7a-a5ec-92663dbf3d49 | invalid_format      | Email address is invalid |
      | 2102003    | 210203 | B23458  | Invalid Structure | user name@nhs.net | 45d7daf4-ec5a-560e-87ba-456aaceca3eb | invalid_format      | Email address is invalid |
