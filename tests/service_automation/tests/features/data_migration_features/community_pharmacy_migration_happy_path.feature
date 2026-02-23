@data-migration
Feature: Data Migration - Community Pharmacy

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

    Then the 'organisation' for service ID '10012345' has content:
      """
      {
        "id": "6ba04c7d-9b6a-5be1-b545-0e77a19e6cf3",
        "identifier_oldDoS_uid": "999999",
        "field": "document",
        "active": true,
        "createdBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "created": "TIMESTAMP",
        "endpoints": [],
        "identifier_ODS_ODSCode": "FXX99",
        "lastUpdatedBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "lastUpdated": "TIMESTAMP",
        "name": "Test Community Pharmacy",
        "telecom": [],
        "type": "Pharmacy",
        "legalDates": null,
        "primary_role_code": null,
        "non_primary_role_codes": []
      }
      """

    Then the 'healthcare-service' for service ID '10012345' has content:
      """
      {
        "id": "49d69102-7da8-5716-aa08-d53badeabbc3",
        "identifier_oldDoS_uid": "999999",
        "field": "document",
        "active": true,
        "ageEligibilityCriteria": null,
        "category": "Pharmacy Services",
        "type": "Essential Services",
        "providedBy": "6ba04c7d-9b6a-5be1-b545-0e77a19e6cf3",
        "location": "62662791-8c06-5f50-980a-eba412cab65d",
        "name": "Test Community Pharmacy",
        "openingTime": [],
        "dispositions": [],
        "symptomGroupSymptomDiscriminators": [],
        "telecom": {
          "phone_public": "01234567890",
          "phone_private": "09876543210",
          "email": "test.pharmacy@nhs.net",
          "web": "www.testpharmacy.com"
        },
        "createdBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "created": "TIMESTAMP",
        "lastUpdatedBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "lastUpdated": "TIMESTAMP"
      }
      """

    Then the 'location' for service ID '10012345' has content:
      """
      {
        "id": "62662791-8c06-5f50-980a-eba412cab65d",
        "identifier_oldDoS_uid": "999999",
        "field": "document",
        "active": true,
        "managingOrganisation": "6ba04c7d-9b6a-5be1-b545-0e77a19e6cf3",
        "address": {
          "county": null,
          "line1": "123 Pharmacy Street",
          "line2": "Test Area",
          "postcode": "TE1 1ST",
          "town": "TESTTOWN"
        },
        "name": null,
        "partOf": null,
        "positionGCS": {
          "latitude": "52.0910543000",
          "longitude": "-1.9510030000"
        },
        "positionReferenceNumber_UBRN": null,
        "positionReferenceNumber_UPRN": null,
        "primaryAddress": true,
        "createdBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "created": "TIMESTAMP",
        "lastUpdatedBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "lastUpdated": "TIMESTAMP"
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

    # Verify initial content
    Then the 'organisation' for service ID '10012346' has content:
      """
      {
        "id": "bc85d805-4456-5311-9b9c-48316e0cce75",
        "identifier_oldDoS_uid": "999998",
        "field": "document",
        "active": true,
        "createdBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "created": "TIMESTAMP",
        "endpoints": [],
        "identifier_ODS_ODSCode": "FXX98",
        "lastUpdatedBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "lastUpdated": "TIMESTAMP",
        "name": "Initial Pharmacy Public Name",
        "telecom": [],
        "type": "Pharmacy",
        "legalDates": null,
        "primary_role_code": null,
        "non_primary_role_codes": []
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

    # Verify updated content - organisation name should be updated
    Then the 'organisation' for service ID '10012346' has content:
      """
      {
        "id": "bc85d805-4456-5311-9b9c-48316e0cce75",
        "identifier_oldDoS_uid": "999998",
        "field": "document",
        "active": true,
        "createdBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "created": "TIMESTAMP",
        "endpoints": [],
        "identifier_ODS_ODSCode": "FXX98",
        "lastUpdatedBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "lastUpdated": "TIMESTAMP",
        "name": "Updated Pharmacy Name",
        "telecom": [],
        "type": "Pharmacy",
        "legalDates": null,
        "primary_role_code": null,
        "non_primary_role_codes": []
      }
      """

    # Verify updated content - healthcare-service name and telecom should be updated
    Then the 'healthcare-service' for service ID '10012346' has content:
      """
      {
        "id": "2a04177f-d83f-5eb6-9711-71eccbe35e49",
        "identifier_oldDoS_uid": "999998",
        "field": "document",
        "active": true,
        "ageEligibilityCriteria": null,
        "category": "Pharmacy Services",
        "type": "Essential Services",
        "providedBy": "bc85d805-4456-5311-9b9c-48316e0cce75",
        "location": "c9068da8-131d-58a1-9e60-ba24c7cfcb06",
        "name": "Updated Service Name",
        "openingTime": [],
        "dispositions": [],
        "symptomGroupSymptomDiscriminators": [],
        "telecom": {
          "phone_public": "03333333333",
          "phone_private": "02222222222",
          "email": "initial@nhs.net",
          "web": "www.initial.com"
        },
        "createdBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "created": "TIMESTAMP",
        "lastUpdatedBy": {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
        "lastUpdated": "TIMESTAMP"
      }
      """
