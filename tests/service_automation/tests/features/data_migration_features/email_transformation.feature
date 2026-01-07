@data-migration
Feature: Email Transformation

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

    When the service migration process is run for table 'services', ID '<service_id>' and method 'insert'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    Then there is 1 organisation, 1 location and 1 healthcare services created
    And the migration state of service ID '<service_id>' contains 0 validation issues
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


  Scenario Outline: Invalid email addresses trigger migration notes
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

    When the service migration process is run for table 'services', ID '<service_id>' and method 'insert'
    Then the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    Then there is 1 organisation, 1 location and 1 healthcare services created
    And the migration state of service ID '<service_id>' contains 1 validation issues
    And the migration state of service ID '<service_id>' has the following validation issues:
      | expression | severity | code         | diagnostics     | value         |
      | email      | error    | <error_code> | <error_message> | <error_value> |
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
      | service_id | uid    | odscode | description       | email             | uuid                                 | error_code       | error_message            | error_value       |
      | 2102001    | 210201 | B23456  | Empty Email       |                   | f0e0264a-7cbd-5f1e-afda-ccc02da9aea3 | email_not_string | Email must be a string   | None              |
      | 2102002    | 210202 | B23457  | Invalid Format    | invalidemail      | 275eea01-a750-5b7a-a5ec-92663dbf3d49 | invalid_format   | Email address is invalid | invalidemail      |
      | 2102003    | 210203 | B23458  | Invalid Structure | user name@nhs.net | 45d7daf4-ec5a-560e-87ba-456aaceca3eb | invalid_format   | Email address is invalid | user name@nhs.net |
