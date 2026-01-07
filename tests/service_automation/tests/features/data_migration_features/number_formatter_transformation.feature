@data-migration
Feature: Number Formatter Transformation

  Scenario: Age ranges with scientific notation are cleaned correctly
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                |
      | id                                  | 3001001                              |
      | uid                                 | 300101                               |
      | name                                | GP: Scientific Notation Test Surgery |
      | odscode                             | A12345                               |
      | openallhours                        | false                                |
      | publicreferralinstructions          |                                      |
      | telephonetriagereferralinstructions | Test referral instructions           |
      | restricttoreferrals                 | true                                 |
      | address                             | Test Surgery$10 Test St$Test City    |
      | town                                | TEST CITY                            |
      | postcode                            | TE1 1ST                              |
      | easting                             | 400001                               |
      | northing                            | 500001                               |
      | publicphone                         | 01234567890                          |
      | nonpublicphone                      |                                      |
      | fax                                 | 01234567891                          |
      | email                               | test@nhs.net                         |
      | web                                 | https://www.test.co.uk/              |
      | createdby                           | HUMAN                                |
      | createdtime                         | 2020-01-01 10:00:00.000              |
      | modifiedby                          | ROBOT                                |
      | modifiedtime                        | 2024-01-01 10:00:00.000              |
      | lasttemplatename                    | Test Template                        |
      | lasttemplateid                      | 100001                               |
      | typeid                              | 100                                  |
      | parentid                            | 1001                                 |
      | subregionid                         | 1001                                 |
      | statusid                            | 1                                    |
      | organisationid                      |                                      |
      | returnifopenminutes                 |                                      |
      | publicname                          | Scientific Notation Test Surgery     |
      | latitude                            | 51.5074                              |
      | longitude                           | -0.1278                              |
      | professionalreferralinfo            |                                      |
      | lastverified                        |                                      |
      | nextverificationdue                 |                                      |
    And a "ServiceAgeRange" exists in DoS with attributes
      | key       | value   | comment                      |
      | id        | 3000001 |                              |
      | daysfrom  | 0E-10   | Scientific notation for zero |
      | daysto    | 4.2E+1  | Scientific notation for 42   |
      | serviceid | 3001001 |                              |
    When the service migration process is run for table 'services', ID '3001001' and method 'insert'
    Then the service migration process completes successfully
    And the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And the 'healthcare-service' for service ID '3001001' contains age eligibility criteria:
      | rangeFrom | rangeTo | type |
      | 0         | 42      | days |

  Scenario: Age ranges with trailing zeros are cleaned correctly
    Given a "Service" exists in DoS with attributes
      | key                                 | value                             |
      | id                                  | 3001002                           |
      | uid                                 | 300102                            |
      | name                                | GP: Trailing Zeros Test Surgery   |
      | odscode                             | B12345                            |
      | openallhours                        | false                             |
      | publicreferralinstructions          |                                   |
      | telephonetriagereferralinstructions | Test referral instructions        |
      | restricttoreferrals                 | true                              |
      | address                             | Test Surgery$20 Test St$Test City |
      | town                                | TEST CITY                         |
      | postcode                            | TE2 2ST                           |
      | easting                             | 400002                            |
      | northing                            | 500002                            |
      | publicphone                         | 01234567890                       |
      | nonpublicphone                      |                                   |
      | fax                                 | 01234567891                       |
      | email                               | test@nhs.net                      |
      | web                                 | https://www.test.co.uk/           |
      | createdby                           | HUMAN                             |
      | createdtime                         | 2020-01-01 10:00:00.000           |
      | modifiedby                          | ROBOT                             |
      | modifiedtime                        | 2024-01-01 10:00:00.000           |
      | lasttemplatename                    | Test Template                     |
      | lasttemplateid                      | 100001                            |
      | typeid                              | 100                               |
      | parentid                            | 1001                              |
      | subregionid                         | 1001                              |
      | statusid                            | 1                                 |
      | organisationid                      |                                   |
      | returnifopenminutes                 |                                   |
      | publicname                          | Trailing Zeros Test Surgery       |
      | latitude                            | 51.5074                           |
      | longitude                           | -0.1278                           |
      | professionalreferralinfo            |                                   |
      | lastverified                        |                                   |
      | nextverificationdue                 |                                   |
    And a "ServiceAgeRange" exists in DoS with attributes
      | key       | value    | comment                     |
      | id        | 3000002  |                             |
      | daysfrom  | 42.4200  | Decimal with trailing zeros |
      | daysto    | 365.2500 | Decimal with trailing zeros |
      | serviceid | 3001002  |                             |
    When the service migration process is run for table 'services', ID '3001002' and method 'insert'
    Then the service migration process completes successfully
    And the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And the 'healthcare-service' for service ID '3001002' contains age eligibility criteria:
      | rangeFrom | rangeTo | type |
      | 42.42     | 365.25  | days |

  Scenario: Age ranges with rounding are handled correctly
    Given a "Service" exists in DoS with attributes
      | key                                 | value                             |
      | id                                  | 3001003                           |
      | uid                                 | 300103                            |
      | name                                | GP: Rounding Test Surgery         |
      | odscode                             | C12345                            |
      | openallhours                        | false                             |
      | publicreferralinstructions          |                                   |
      | telephonetriagereferralinstructions | Test referral instructions        |
      | restricttoreferrals                 | true                              |
      | address                             | Test Surgery$30 Test St$Test City |
      | town                                | TEST CITY                         |
      | postcode                            | TE3 3ST                           |
      | easting                             | 400003                            |
      | northing                            | 500003                            |
      | publicphone                         | 01234567890                       |
      | nonpublicphone                      |                                   |
      | fax                                 | 01234567891                       |
      | email                               | test@nhs.net                      |
      | web                                 | https://www.test.co.uk/           |
      | createdby                           | HUMAN                             |
      | createdtime                         | 2020-01-01 10:00:00.000           |
      | modifiedby                          | ROBOT                             |
      | modifiedtime                        | 2024-01-01 10:00:00.000           |
      | lasttemplatename                    | Test Template                     |
      | lasttemplateid                      | 100001                            |
      | typeid                              | 100                               |
      | parentid                            | 1001                              |
      | subregionid                         | 1001                              |
      | statusid                            | 1                                 |
      | organisationid                      |                                   |
      | returnifopenminutes                 |                                   |
      | publicname                          | Rounding Test Surgery             |
      | latitude                            | 51.5074                           |
      | longitude                           | -0.1278                           |
      | professionalreferralinfo            |                                   |
      | lastverified                        |                                   |
      | nextverificationdue                 |                                   |
    And a "ServiceAgeRange" exists in DoS with attributes
      | key       | value     | comment                                  |
      | id        | 3000003   |                                          |
      | daysfrom  | 42.426789 | More than 2 decimal places - rounds up   |
      | daysto    | 365.423   | More than 2 decimal places - rounds down |
      | serviceid | 3001003   |                                          |
    When the service migration process is run for table 'services', ID '3001003' and method 'insert'
    Then the service migration process completes successfully
    And the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And the 'healthcare-service' for service ID '3001003' contains age eligibility criteria:
      | rangeFrom | rangeTo | type |
      | 42.43     | 365.42  | days |

  Scenario: Position GCS coordinates with many decimal places are cleaned
    Given a "Service" exists in DoS with attributes
      | key                                 | value                             |
      | id                                  | 3001004                           |
      | uid                                 | 300104                            |
      | name                                | GP: Precise Coordinates Test      |
      | odscode                             | D12345                            |
      | openallhours                        | false                             |
      | publicreferralinstructions          |                                   |
      | telephonetriagereferralinstructions | Test referral instructions        |
      | restricttoreferrals                 | true                              |
      | address                             | Test Surgery$40 Test St$Test City |
      | town                                | TEST CITY                         |
      | postcode                            | TE4 4ST                           |
      | easting                             | 400004                            |
      | northing                            | 500004                            |
      | publicphone                         | 01234567890                       |
      | nonpublicphone                      |                                   |
      | fax                                 | 01234567891                       |
      | email                               | test@nhs.net                      |
      | web                                 | https://www.test.co.uk/           |
      | createdby                           | HUMAN                             |
      | createdtime                         | 2020-01-01 10:00:00.000           |
      | modifiedby                          | ROBOT                             |
      | modifiedtime                        | 2024-01-01 10:00:00.000           |
      | lasttemplatename                    | Test Template                     |
      | lasttemplateid                      | 100001                            |
      | typeid                              | 100                               |
      | parentid                            | 1001                              |
      | subregionid                         | 1001                              |
      | statusid                            | 1                                 |
      | organisationid                      |                                   |
      | returnifopenminutes                 |                                   |
      | publicname                          | Precise Coordinates Test          |
      | latitude                            | 51.50740123456789                 |
      | longitude                           | -0.12780987654321                 |
      | professionalreferralinfo            |                                   |
      | lastverified                        |                                   |
      | nextverificationdue                 |                                   |
    When the service migration process is run for table 'services', ID '3001004' and method 'insert'
    Then the service migration process completes successfully
    And the metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped, 0 invalid and 0 errored
    And field 'positionGCS' on table 'location' for id '8d5c9c84-53e6-5b68-ae55-6c82d8f4c881' should have cleaned coordinates
