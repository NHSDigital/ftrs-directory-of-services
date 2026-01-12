@data-migration @incremental-update
Feature: Incremental Updates - Location Field Changes
  Tests for verifying incremental updates to Location entity fields

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Update location address line
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 520001                  |
      | uid                 | 520001                  |
      | name                | Address Update Practice |
      | odscode             | C52001                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 100 Original Street     |
      | town                | ORIGINALTOWN            |
      | postcode            | LO1 1AA                 |
      | publicphone         | 01234 100001            |
      | email               | loc1@nhs.net            |
      | web                 | www.loc1.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Address Update Practice |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '520001' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520001' with version 1
    And field 'address' on table 'location' for id 'e9e10ca4-7c9a-5251-8a48-a73cd0a4a94e' has content:
      """
      {
        "address": {
          "line1": "100 Original Street",
          "line2": null,
          "town": "ORIGINALTOWN",
          "county": null,
          "postcode": "LO1 1AA"
        }
      }
      """

    Given the "Service" with id "520001" is updated with attributes
      | key     | value              |
      | address | 200 Updated Street |

    When the data migration process is run for table 'services', ID '520001' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520001' with version 2
    And field 'address' on table 'location' for id 'e9e10ca4-7c9a-5251-8a48-a73cd0a4a94e' has content:
      """
      {
        "address": {
          "line1": "200 Updated Street",
          "line2": null,
          "town": "ORIGINALTOWN",
          "county": null,
          "postcode": "LO1 1AA"
        }
      }
      """

  Scenario: Update location town
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 520002                  |
      | uid                 | 520002                  |
      | name                | Town Update Practice    |
      | odscode             | C52002                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 101 Service Street      |
      | town                | OLDTOWN                 |
      | postcode            | LO1 2AA                 |
      | publicphone         | 01234 100002            |
      | email               | loc2@nhs.net            |
      | web                 | www.loc2.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Town Update Practice    |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '520002' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520002' with version 1
    And field 'address' on table 'location' for id 'd1d1d58f-c325-5c76-aa7c-3bf4b25b33b8' has content:
      """
      {
        "address": {
          "line1": "101 Service Street",
          "line2": null,
          "town": "OLDTOWN",
          "county": null,
          "postcode": "LO1 2AA"
        }
      }
      """

    Given the "Service" with id "520002" is updated with attributes
      | key  | value   |
      | town | NEWTOWN |

    When the data migration process is run for table 'services', ID '520002' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520002' with version 2
    And field 'address' on table 'location' for id 'd1d1d58f-c325-5c76-aa7c-3bf4b25b33b8' has content:
      """
      {
        "address": {
          "line1": "101 Service Street",
          "line2": null,
          "town": "NEWTOWN",
          "county": null,
          "postcode": "LO1 2AA"
        }
      }
      """

  Scenario: Update location postcode
    Given a "Service" exists in DoS with attributes
      | key                 | value                    |
      | id                  | 520003                   |
      | uid                 | 520003                   |
      | name                | Postcode Update Practice |
      | odscode             | C52003                   |
      | openallhours        | FALSE                    |
      | restricttoreferrals | FALSE                    |
      | address             | 102 Service Street       |
      | town                | SERVICETOWN              |
      | postcode            | AB1 1CD                  |
      | publicphone         | 01234 100003             |
      | email               | loc3@nhs.net             |
      | web                 | www.loc3.com             |
      | createdtime         | 2024-01-01 08:00:00.000  |
      | modifiedtime        | 2024-01-01 08:00:00.000  |
      | typeid              | 100                      |
      | statusid            | 1                        |
      | publicname          | Postcode Update Practice |
      | latitude            | 51.5074                  |
      | longitude           | -0.1278                  |

    When the data migration process is run for table 'services', ID '520003' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520003' with version 1
    And field 'address' on table 'location' for id 'd96ddd15-5187-580c-aefa-c3f6b463cf91' has content:
      """
      {
        "address": {
          "line1": "102 Service Street",
          "line2": null,
          "town": "SERVICETOWN",
          "county": null,
          "postcode": "AB1 1CD"
        }
      }
      """

    Given the "Service" with id "520003" is updated with attributes
      | key      | value   |
      | postcode | XY9 8ZW |

    When the data migration process is run for table 'services', ID '520003' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520003' with version 2
    And field 'address' on table 'location' for id 'd96ddd15-5187-580c-aefa-c3f6b463cf91' has content:
      """
      {
        "address": {
          "line1": "102 Service Street",
          "line2": null,
          "town": "SERVICETOWN",
          "county": null,
          "postcode": "XY9 8ZW"
        }
      }
      """

  Scenario: Update complete address (line, town, and postcode)
    Given a "Service" exists in DoS with attributes
      | key                 | value                        |
      | id                  | 520004                       |
      | uid                 | 520004                       |
      | name                | Full Address Update Practice |
      | odscode             | C52004                       |
      | openallhours        | FALSE                        |
      | restricttoreferrals | FALSE                        |
      | address             | 1 Old Street                 |
      | town                | OLDCITY                      |
      | postcode            | OL1 1AA                      |
      | publicphone         | 01234 100004                 |
      | email               | loc4@nhs.net                 |
      | web                 | www.loc4.com                 |
      | createdtime         | 2024-01-01 08:00:00.000      |
      | modifiedtime        | 2024-01-01 08:00:00.000      |
      | typeid              | 100                          |
      | statusid            | 1                            |
      | publicname          | Full Address Update Practice |
      | latitude            | 51.5074                      |
      | longitude           | -0.1278                      |

    When the data migration process is run for table 'services', ID '520004' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520004' with version 1
    And field 'address' on table 'location' for id 'bbaadb8a-5c7c-5589-bfac-adb3d01c8b66' has content:
      """
      {
        "address": {
          "line1": "1 Old Street",
          "line2": null,
          "town": "OLDCITY",
          "county": null,
          "postcode": "OL1 1AA"
        }
      }
      """

    Given the "Service" with id "520004" is updated with attributes
      | key      | value          |
      | address  | 999 New Avenue |
      | town     | NEWCITY        |
      | postcode | NE9 9ZZ        |

    When the data migration process is run for table 'services', ID '520004' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520004' with version 2
    And field 'address' on table 'location' for id 'bbaadb8a-5c7c-5589-bfac-adb3d01c8b66' has content:
      """
      {
        "address": {
          "line1": "999 New Avenue",
          "line2": null,
          "town": "NEWCITY",
          "county": null,
          "postcode": "NE9 9ZZ"
        }
      }
      """

  Scenario: Update location latitude (position GCS change)
    Given a "Service" exists in DoS with attributes
      | key                 | value                    |
      | id                  | 520005                   |
      | uid                 | 520005                   |
      | name                | Latitude Update Practice |
      | odscode             | C52005                   |
      | openallhours        | FALSE                    |
      | restricttoreferrals | FALSE                    |
      | address             | 103 Service Street       |
      | town                | SERVICETOWN              |
      | postcode            | LO1 5AA                  |
      | publicphone         | 01234 100005             |
      | email               | loc5@nhs.net             |
      | web                 | www.loc5.com             |
      | createdtime         | 2024-01-01 08:00:00.000  |
      | modifiedtime        | 2024-01-01 08:00:00.000  |
      | typeid              | 100                      |
      | statusid            | 1                        |
      | publicname          | Latitude Update Practice |
      | latitude            | 51.5074                  |
      | longitude           | -0.1278                  |

    When the data migration process is run for table 'services', ID '520005' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520005' with version 1
    And field 'positionGCS' on table 'location' for id '8ae47209-5284-51bd-82fd-29f66ab7d69e' has content:
      """
      {
        "positionGCS": {
          "latitude": "51.5074000000",
          "longitude": "-0.1278000000"
        }
      }
      """

    Given the "Service" with id "520005" is updated with attributes
      | key      | value   |
      | latitude | 52.4862 |

    When the data migration process is run for table 'services', ID '520005' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520005' with version 2
    And field 'positionGCS' on table 'location' for id '8ae47209-5284-51bd-82fd-29f66ab7d69e' has content:
      """
      {
        "positionGCS": {
          "latitude": "52.4862000000",
          "longitude": "-0.1278000000"
        }
      }
      """

  Scenario: Update location longitude (position GCS change)
    Given a "Service" exists in DoS with attributes
      | key                 | value                     |
      | id                  | 520006                    |
      | uid                 | 520006                    |
      | name                | Longitude Update Practice |
      | odscode             | C52006                    |
      | openallhours        | FALSE                     |
      | restricttoreferrals | FALSE                     |
      | address             | 104 Service Street        |
      | town                | SERVICETOWN               |
      | postcode            | LO1 6AA                   |
      | publicphone         | 01234 100006              |
      | email               | loc6@nhs.net              |
      | web                 | www.loc6.com              |
      | createdtime         | 2024-01-01 08:00:00.000   |
      | modifiedtime        | 2024-01-01 08:00:00.000   |
      | typeid              | 100                       |
      | statusid            | 1                         |
      | publicname          | Longitude Update Practice |
      | latitude            | 51.5074                   |
      | longitude           | -0.1278                   |

    When the data migration process is run for table 'services', ID '520006' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520006' with version 1
    And field 'positionGCS' on table 'location' for id '4da5fd94-4cc5-5818-a259-b5c3b10c2776' has content:
      """
      {
        "positionGCS": {
          "latitude": "51.5074000000",
          "longitude": "-0.1278000000"
        }
      }
      """

    Given the "Service" with id "520006" is updated with attributes
      | key       | value   |
      | longitude | -1.8904 |

    When the data migration process is run for table 'services', ID '520006' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520006' with version 2
    And field 'positionGCS' on table 'location' for id '4da5fd94-4cc5-5818-a259-b5c3b10c2776' has content:
      """
      {
        "positionGCS": {
          "latitude": "51.5074000000",
          "longitude": "-1.8904000000"
        }
      }
      """

  Scenario: Update both latitude and longitude (complete position change)
    Given a "Service" exists in DoS with attributes
      | key                 | value                    |
      | id                  | 520007                   |
      | uid                 | 520007                   |
      | name                | Position Update Practice |
      | odscode             | C52007                   |
      | openallhours        | FALSE                    |
      | restricttoreferrals | FALSE                    |
      | address             | 105 Service Street       |
      | town                | SERVICETOWN              |
      | postcode            | LO1 7AA                  |
      | publicphone         | 01234 100007             |
      | email               | loc7@nhs.net             |
      | web                 | www.loc7.com             |
      | createdtime         | 2024-01-01 08:00:00.000  |
      | modifiedtime        | 2024-01-01 08:00:00.000  |
      | typeid              | 100                      |
      | statusid            | 1                        |
      | publicname          | Position Update Practice |
      | latitude            | 51.5074                  |
      | longitude           | -0.1278                  |

    When the data migration process is run for table 'services', ID '520007' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520007' with version 1
    And field 'positionGCS' on table 'location' for id '7821cd29-abe2-5703-9775-b059db21ca34' has content:
      """
      {
        "positionGCS": {
          "latitude": "51.5074000000",
          "longitude": "-0.1278000000"
        }
      }
      """

    Given the "Service" with id "520007" is updated with attributes
      | key       | value   |
      | latitude  | 53.4808 |
      | longitude | -2.2426 |

    When the data migration process is run for table 'services', ID '520007' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520007' with version 2
    And field 'positionGCS' on table 'location' for id '7821cd29-abe2-5703-9775-b059db21ca34' has content:
      """
      {
        "positionGCS": {
          "latitude": "53.4808000000",
          "longitude": "-2.2426000000"
        }
      }
      """

  Scenario: Update address and coordinates together
    Given a "Service" exists in DoS with attributes
      | key                 | value                   |
      | id                  | 520008                  |
      | uid                 | 520008                  |
      | name                | Relocation Practice     |
      | odscode             | C52008                  |
      | openallhours        | FALSE                   |
      | restricttoreferrals | FALSE                   |
      | address             | 1 London Road           |
      | town                | LONDON                  |
      | postcode            | E1 1AA                  |
      | publicphone         | 01234 100008            |
      | email               | loc8@nhs.net            |
      | web                 | www.loc8.com            |
      | createdtime         | 2024-01-01 08:00:00.000 |
      | modifiedtime        | 2024-01-01 08:00:00.000 |
      | typeid              | 100                     |
      | statusid            | 1                       |
      | publicname          | Relocation Practice     |
      | latitude            | 51.5074                 |
      | longitude           | -0.1278                 |

    When the data migration process is run for table 'services', ID '520008' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520008' with version 1
    And field 'positionGCS' on table 'location' for id 'cc845dc8-a2ba-5710-95e4-efd6e120a9fc' has content:
      """
      {
        "positionGCS": {
          "latitude": "51.5074000000",
          "longitude": "-0.1278000000"
        }
      }
      """
    And field 'address' on table 'location' for id 'cc845dc8-a2ba-5710-95e4-efd6e120a9fc' has content:
      """
      {
        "address": {
          "line1": "1 London Road",
          "line2": null,
          "town": "LONDON",
          "county": null,
          "postcode": "E1 1AA"
        }
      }
      """


    Given the "Service" with id "520008" is updated with attributes
      | key       | value              |
      | address   | 99 Manchester Road |
      | town      | MANCHESTER         |
      | postcode  | M1 9ZZ             |
      | latitude  | 53.4808            |
      | longitude | -2.2426            |

    When the data migration process is run for table 'services', ID '520008' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#520008' with version 2
    And field 'positionGCS' on table 'location' for id 'cc845dc8-a2ba-5710-95e4-efd6e120a9fc' has content:
      """
      {
        "positionGCS": {
          "latitude": "53.4808000000",
          "longitude": "-2.2426000000"
        }
      }
      """
    And field 'address' on table 'location' for id 'cc845dc8-a2ba-5710-95e4-efd6e120a9fc' has content:
      """
      {
        "address": {
          "line1": "99 Manchester Road",
          "line2": null,
          "town": "MANCHESTER",
          "county": null,
          "postcode": "M1 9ZZ"
        }
      }
      """
