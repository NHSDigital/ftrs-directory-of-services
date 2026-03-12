@data-migration
Feature: Data Migration - Pharmacy

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  @happy
  Scenario: Happy path migration for a Community Pharmacy
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 10012345                                                 |
      | uid                                 | 999999                                                   |
      | name                                | Test Community Pharmacy                                  |
      | odscode                             | FXX99                                                    |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 12345        |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text 12345   |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 123 Pharmacy Street$Test Area$Test City                  |
      | town                                | TESTTOWN                                                 |
      | postcode                            | TE1 1ST                                                  |
      | easting                             | 403453                                                   |
      | northing                            | 243634                                                   |
      | publicphone                         | 01234 567890                                             |
      | nonpublicphone                      | 09876 543210                                             |
      | fax                                 |                                                          |
      | email                               | test.pharmacy@nhs.net                                    |
      | web                                 | www.testpharmacy.com                                     |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2020-01-15 08:00:51.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                  |
      | lasttemplatename                    | Pharmacy Template                                        |
      | lasttemplateid                      | 244764                                                   |
      | typeid                              | 13                                                       |
      | parentid                            | 150013                                                   |
      | subregionid                         | 150013                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Test Community Pharmacy                                  |
      | latitude                            | 52.0910543                                               |
      | longitude                           | -1.951003                                                |
      | professionalreferralinfo            | Professional referral information for pharmacy           |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    When the data migration process is run for table 'services', ID '10012345' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then the state table contains a record for key 'services#10012345' with version 1

    # Validate key properties to verify integration (detailed transformation logic is covered by unit tests)
    Then the 'organisation' for service ID '10012345' has content:
      """
      {
        "id": "6ba04c7d-9b6a-5be1-b545-0e77a19e6cf3",
        "identifier_oldDoS_uid": "999999",
        "identifier_ODS_ODSCode": "FXX99",
        "name": "Test Community Pharmacy",
        "type": "Community Pharmacy",
        "active": true
      }
      """

    Then the 'healthcare-service' for service ID '10012345' has content:
      """
      {
        "id": "49d69102-7da8-5716-aa08-d53badeabbc3",
        "identifier_oldDoS_uid": "999999",
        "providedBy": "6ba04c7d-9b6a-5be1-b545-0e77a19e6cf3",
        "location": "62662791-8c06-5f50-980a-eba412cab65d",
        "name": "Test Community Pharmacy",
        "category": "Pharmacy Services",
        "type": "Essential Services",
        "status": "active"
      }
      """

    Then the 'location' for service ID '10012345' has content:
      """
      {
        "id": "62662791-8c06-5f50-980a-eba412cab65d",
        "identifier_oldDoS_uid": "999999",
        "managingOrganisation": "6ba04c7d-9b6a-5be1-b545-0e77a19e6cf3",
        "active": true
      }
      """

  @incremental-update
  Scenario: Incremental update for a Community Pharmacy with data changes
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 10012346                                                 |
      | uid                                 | 999998                                                   |
      | name                                | Initial Pharmacy Name                                    |
      | odscode                             | FXX98                                                    |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          | STUB Public Referral Instruction                         |
      | telephonetriagereferralinstructions | STUB Telephone Triage                                    |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 456 Initial Street$Initial Area$Initial City             |
      | town                                | INITIALTOWN                                              |
      | postcode                            | IN1 1AL                                                  |
      | easting                             | 403453                                                   |
      | northing                            | 243634                                                   |
      | publicphone                         | 01111 111111                                             |
      | nonpublicphone                      | 02222 222222                                             |
      | fax                                 |                                                          |
      | email                               | initial@nhs.net                                          |
      | web                                 | www.initial.com                                          |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2020-01-15 08:00:51.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                  |
      | lasttemplatename                    | Pharmacy Template                                        |
      | lasttemplateid                      | 244764                                                   |
      | typeid                              | 13                                                       |
      | parentid                            | 150013                                                   |
      | subregionid                         | 150013                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Initial Pharmacy Public Name                             |
      | latitude                            | 52.0910543                                               |
      | longitude                           | -1.951003                                                |
      | professionalreferralinfo            | Initial professional info                                |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    # Initial migration (INSERT)
    When the data migration process is run for table 'services', ID '10012346' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 1 healthcare services created
    And the state table contains a record for key 'services#10012346' with version 1

    # Verify initial key properties
    Then the 'organisation' for service ID '10012346' has content:
      """
      {
        "id": "bc85d805-4456-5311-9b9c-48316e0cce75",
        "identifier_oldDoS_uid": "999998",
        "identifier_ODS_ODSCode": "FXX98",
        "name": "Initial Pharmacy Public Name",
        "type": "Community Pharmacy",
        "active": true
      }
      """

    # Update the DoS source data
    Given the "Service" with id "10012346" is updated with attributes
      | key        | value                |
      | publicname | Updated Pharmacy Name|
      | name       | Updated Service Name |
      | publicphone| 03333 333333         |

    # Re-run migration (UPDATE with changes)
    When the data migration process is run for table 'services', ID '10012346' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#10012346' with version 2

    # Verify updated fields - focus on changed properties only
    Then the 'organisation' for service ID '10012346' has content:
      """
      {
        "id": "bc85d805-4456-5311-9b9c-48316e0cce75",
        "name": "Updated Pharmacy Name"
      }
      """

    Then the 'healthcare-service' for service ID '10012346' has content:
      """
      {
        "id": "2a04177f-d83f-5eb6-9711-71eccbe35e49",
        "name": "Updated Service Name"
      }
      """

  @happy
  Scenario: Happy path migration for a Distance Selling Pharmacy
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 10012348                                                 |
      | uid                                 | 999996                                                   |
      | name                                | Test Distance Selling Pharmacy                           |
      | odscode                             | FXX96                                                    |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 12348        |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text 12348   |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 123 Distance Pharmacy Street$Test Area$Test City         |
      | town                                | TESTTOWN                                                 |
      | postcode                            | TE3 3ST                                                  |
      | easting                             | 403453                                                   |
      | northing                            | 243634                                                   |
      | publicphone                         | 01234 567891                                             |
      | nonpublicphone                      | 09876 543211                                             |
      | fax                                 |                                                          |
      | email                               | distance.pharmacy@nhs.net                                |
      | web                                 | www.distancepharmacy.com                                 |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2020-01-15 08:00:51.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                  |
      | lasttemplatename                    | Distance Selling Pharmacy Template                       |
      | lasttemplateid                      | 244765                                                   |
      | typeid                              | 134                                                      |
      | parentid                            | 150013                                                   |
      | subregionid                         | 150013                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Test Distance Selling Pharmacy                           |
      | latitude                            | 52.0910543                                               |
      | longitude                           | -1.951003                                                |
      | professionalreferralinfo            | Professional referral information for distance selling   |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    When the data migration process is run for table 'services', ID '10012348' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then the state table contains a record for key 'services#10012348' with version 1

    # Validate key properties to verify integration (detailed transformation logic is covered by unit tests)
    Then the 'organisation' for service ID '10012348' has content:
      """
      {
        "id": "79da7fc6-9cd7-5405-baed-81cfa1717ad3",
        "identifier_oldDoS_uid": "999996",
        "identifier_ODS_ODSCode": "FXX96",
        "name": "Test Distance Selling Pharmacy",
        "type": "Distance Selling Pharmacy",
        "active": true
      }
      """

    Then the 'healthcare-service' for service ID '10012348' has content:
      """
      {
        "id": "43707340-6d35-5a96-812e-570e5bbf88e1",
        "identifier_oldDoS_uid": "999996",
        "providedBy": "79da7fc6-9cd7-5405-baed-81cfa1717ad3",
        "location": "ab0241ba-6e3b-5d93-9e53-9260e9466307",
        "name": "Test Distance Selling Pharmacy",
        "category": "Pharmacy Services",
        "type": "Essential Services",
        "status": "active"
      }
      """

    Then the 'location' for service ID '10012348' has content:
      """
      {
        "id": "ab0241ba-6e3b-5d93-9e53-9260e9466307",
        "identifier_oldDoS_uid": "999996",
        "managingOrganisation": "79da7fc6-9cd7-5405-baed-81cfa1717ad3",
        "active": true
      }
      """

  @incremental-update
  Scenario: Incremental update for a Distance Selling Pharmacy with data changes
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                    |
      | id                                  | 10012349                                                 |
      | uid                                 | 999995                                                   |
      | name                                | Initial Distance Pharmacy Name                           |
      | odscode                             | FXX95                                                    |
      | openallhours                        | FALSE                                                    |
      | publicreferralinstructions          | STUB Public Referral Instruction                         |
      | telephonetriagereferralinstructions | STUB Telephone Triage                                    |
      | restricttoreferrals                 | FALSE                                                    |
      | address                             | 456 Initial Street$Initial Area$Initial City             |
      | town                                | INITIALTOWN                                              |
      | postcode                            | IN2 2AL                                                  |
      | easting                             | 403453                                                   |
      | northing                            | 243634                                                   |
      | publicphone                         | 01111 111112                                             |
      | nonpublicphone                      | 02222 222223                                             |
      | fax                                 |                                                          |
      | email                               | initialdistance@nhs.net                                  |
      | web                                 | www.initialdistance.com                                  |
      | createdby                           | HUMAN                                                    |
      | createdtime                         | 2020-01-15 08:00:51.000                                  |
      | modifiedby                          | HUMAN                                                    |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                  |
      | lasttemplatename                    | Distance Selling Pharmacy Template                       |
      | lasttemplateid                      | 244765                                                   |
      | typeid                              | 134                                                      |
      | parentid                            | 150013                                                   |
      | subregionid                         | 150013                                                   |
      | statusid                            | 1                                                        |
      | organisationid                      |                                                          |
      | returnifopenminutes                 |                                                          |
      | publicname                          | Initial Distance Pharmacy Public Name                    |
      | latitude                            | 52.0910543                                               |
      | longitude                           | -1.951003                                                |
      | professionalreferralinfo            | Initial professional info                                |
      | lastverified                        |                                                          |
      | nextverificationdue                 |                                                          |

    # Initial migration (INSERT)
    When the data migration process is run for table 'services', ID '10012349' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 1 healthcare services created
    And the state table contains a record for key 'services#10012349' with version 1

    # Verify initial key properties
    Then the 'organisation' for service ID '10012349' has content:
      """
      {
        "id": "269d561d-4de8-51b6-a9d8-7f69b9d9cf4a",
        "identifier_oldDoS_uid": "999995",
        "identifier_ODS_ODSCode": "FXX95",
        "name": "Initial Distance Pharmacy Public Name",
        "type": "Distance Selling Pharmacy",
        "active": true
      }
      """

    # Update the DoS source data
    Given the "Service" with id "10012349" is updated with attributes
      | key        | value                         |
      | publicname | Updated Distance Pharmacy Name|
      | name       | Updated Distance Service Name |
      | publicphone| 03333 333334                  |

    # Re-run migration (UPDATE with changes)
    When the data migration process is run for table 'services', ID '10012349' and method 'update'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 0 inserted, 1 updated, 0 skipped and 0 errors
    And the state table contains a record for key 'services#10012349' with version 2

    # Verify updated fields - focus on changed properties only
    Then the 'organisation' for service ID '10012349' has content:
      """
      {
        "id": "269d561d-4de8-51b6-a9d8-7f69b9d9cf4a",
        "name": "Updated Distance Pharmacy Name"
      }
      """

    Then the 'healthcare-service' for service ID '10012349' has content:
      """
      {
        "id": "8662d853-70f5-5e06-bb9b-fd9ed963c0ae",
        "name": "Updated Distance Service Name"
      }
      """
