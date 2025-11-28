@data-migration
Feature: Data Migration

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Happy path migration for a GP Practice
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                                                                                                                                                                                                   |
      | id                                  | 10005752                                                                                                                                                                                                                                |
      | uid                                 | 138179                                                                                                                                                                                                                                  |
      | name                                | Abbey Medical Practice, Evesham, Worcestershire                                                                                                                                                                                         |
      | odscode                             | M81094                                                                                                                                                                                                                                  |
      | openallhours                        | FALSE                                                                                                                                                                                                                                   |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 5752                                                                                                                                                                                        |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 5752                                                                                                                                                                             |
      | restricttoreferrals                 | TRUE                                                                                                                                                                                                                                    |
      | address                             | Evesham Medical Centre$Abbey Lane$Evesham                                                                                                                                                                                               |
      | town                                | EVESHAM                                                                                                                                                                                                                                 |
      | postcode                            | WR11 4BS                                                                                                                                                                                                                                |
      | easting                             | 403453                                                                                                                                                                                                                                  |
      | northing                            | 243634                                                                                                                                                                                                                                  |
      | publicphone                         | 01386 761111                                                                                                                                                                                                                            |
      | nonpublicphone                      | 99999 000000                                                                                                                                                                                                                            |
      | fax                                 | 77777 000000                                                                                                                                                                                                                            |
      | email                               |                                                                                                                                                                                                                                         |
      | web                                 | www.abbeymedical.com                                                                                                                                                                                                                    |
      | createdby                           | HUMAN                                                                                                                                                                                                                                   |
      | createdtime                         | 2011-06-29 08:00:51.000                                                                                                                                                                                                                 |
      | modifiedby                          | HUMAN                                                                                                                                                                                                                                   |
      | modifiedtime                        | 2024-11-29 10:55:23.000                                                                                                                                                                                                                 |
      | lasttemplatename                    | Midlands template R46 Append PC                                                                                                                                                                                                         |
      | lasttemplateid                      | 244764                                                                                                                                                                                                                                  |
      | typeid                              | 100                                                                                                                                                                                                                                     |
      | parentid                            | 150013                                                                                                                                                                                                                                  |
      | subregionid                         | 150013                                                                                                                                                                                                                                  |
      | statusid                            | 1                                                                                                                                                                                                                                       |
      | organisationid                      |                                                                                                                                                                                                   |
      | returnifopenminutes                 |                                                                                                                                                                                                                                         |
      | publicname                          | Abbey Medical Practice                                                                                                                                                                                                                  |
      | latitude                            | 52.0910543                                                                                                                                                                                                                              |
      | longitude                           | -1.951003                                                                                                                                                                                                                               |
      | professionalreferralinfo            | Non-public numbers are for healthcare professionals ONLY; they are not for routine contact and must not be shared with patients\n* GP practice opening hours are 08:00-18:30, hours shown on DoS may vary for administration purposes." |
      | lastverified                        |                                                                                                                                                                                                                                         |
      | nextverificationdue                 |                                                                                                                                                                                                                                         |

    When the data migration process is run for table 'services', ID '10005752' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 1 organisation, 1 location and 1 healthcare services created
    Then the 'organisation' for service ID '10005752' has content:
      """
      {
        "id": "92c51dc4-9b80-54c1-bfcf-62826d6823f0",
        "field": "document",
        "active": true,
        "createdBy": "DATA_MIGRATION",
        "createdDateTime": "2025-10-07T08:38:57.679754Z",
        "endpoints": [],
        "identifier_ODS_ODSCode": "M81094",
        "modifiedBy": "DATA_MIGRATION",
        "modifiedDateTime": "2025-10-07T08:38:57.679754Z",
        "name": "Abbey Medical Practice",
        "telecom": null,
        "type": "GP Practice"
      }
      """
    Then the 'healthcare-service' for service ID '10005752' has content:
      """
      {
        "id": "48865e3d-b8f0-508b-8520-29b3113da1e3",
        "field": "document",
        "active": true,
        "ageEligibilityCriteria": null,
        "category": "GP Services",
        "createdBy": "DATA_MIGRATION",
        "createdDateTime": "2025-10-07T08:38:57.679754Z",
        "dispositions": [],
        "identifier_oldDoS_uid": "138179",
        "location": "fbb2340b-53e0-56f9-ada3-ef5728ca8f98",
        "migrationNotes": [
          "field:['email'] ,error: email_not_string,message:Email must be a string,value:None",
          "field:['nonpublicphone'] ,error: invalid_format,message:Phone number is invalid,value:99999000000"
        ],
        "modifiedBy": "DATA_MIGRATION",
        "modifiedDateTime": "2025-10-07T08:38:57.679754Z",
        "name": "Abbey Medical Practice, Evesham, Worcestershire",
        "openingTime": [],
        "providedBy": "92c51dc4-9b80-54c1-bfcf-62826d6823f0",
        "symptomGroupSymptomDiscriminators": [],
        "telecom": {
          "email": null,
          "phone_private": null,
          "phone_public": "01386761111",
          "web": "www.abbeymedical.com"
        },
        "type": "GP Consultation Service"
      }
      """
    Then the 'location' for service ID '10005752' has content:
      """
      {
        "id": "fbb2340b-53e0-56f9-ada3-ef5728ca8f98",
        "field": "document",
        "active": true,
        "address": {
          "county": null,
          "line1": "Evesham Medical Centre",
          "line2": "Abbey Lane",
          "postcode": "WR11 4BS",
          "town": "EVESHAM"
        },
        "createdBy": "DATA_MIGRATION",
        "createdDateTime": "2025-11-13T15:39:53.539806Z",
        "managingOrganisation": "92c51dc4-9b80-54c1-bfcf-62826d6823f0",
        "modifiedBy": "DATA_MIGRATION",
        "modifiedDateTime": "2025-11-13T15:39:53.539806Z",
        "name": null,
        "partOf": null,
        "positionGCS": {
          "latitude": "52.0910543000",
          "longitude": "-1.9510030000"
        },
        "positionReferenceNumber_UBRN": null,
        "positionReferenceNumber_UPRN": null,
        "primaryAddress": true
      }
      """
