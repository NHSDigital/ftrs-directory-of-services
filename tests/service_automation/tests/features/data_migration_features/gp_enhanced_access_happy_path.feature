@data-migration
Feature: Data Migration

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Happy path migration for a GP Enhanced Access
     Given a 'Service' exists called 'TestGPPractice' in DoS with attributes:
      | key                                 | value                                                         |
      | id                                  | 100178970                                                     |
      | uid                                 | 2000094797                                                    |
      | name                                | PCN - Enhanced Access Hub, Sandwell                           |
      | odscode                             | U31548                                                        |
      | isnational                          |                                                               |
      | openallhours                        | FALSE                                                         |
      | publicreferralinstructions          | STUB Public Referral Instruction Text Field 178970            |
      | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 178970 |
      | restricttoreferrals                 | TRUE                                                          |
      | address                             | Postcode for lookup purpose only                              |
      | town                                | WEDNESBURY                                                    |
      | postcode                            | WS10 0JS                                                      |
      | easting                             | 400927                                                        |
      | northing                            | 295144                                                        |
      | publicphone                         |                                                               |
      | nonpublicphone                      | 99999 000000                                                  |
      | fax                                 |                                                               |
      | email                               | 178970-fake@nhs.gov.uk                                        |
      | web                                 |                                                               |
      | createdby                           | HUMAN                                                         |
      | createdtime                         | 2022-02-11 15:36:15.000                                       |
      | modifiedby                          | HUMAN                                                         |
      | modifiedtime                        | 2025-02-14 11:47:40.000                                       |
      | lasttemplatename                    | PCN - Enhanced Access Hub, Sandwell                           |
      | lasttemplateid                      | 246421                                                        |
      | typeid                              | 152                                                           |
      | parentid                            | 162870                                                        |
      | subregionid                         | 98096                                                         |
      | statusid                            | 1                                                             |
      | organisationid                      |                                                               |
      | returnifopenminutes                 |                                                               |
      | publicname                          | PCN - Enhanced Access Hub, Sandwell                           |
      | latitude                            | 52.5541526                                                    |
      | longitude                           | -1.9877538                                                    |
      | professionalreferralinfo            |                                                               |
      | lastverified                        |                                                               |
      | nextverificationdue                 |                                                               |

    When the data migration process is run with the event:
      """
      {
        "Records": [
          {
            "messageId": "test-message-1",
            "receiptHandle": "test-receipt-handle",
            "body": "{\"type\": \"dms_event\", \"record_id\": 100178970, \"table_name\": \"services\", \"method\": \"insert\"}",
            "attributes": {
              "ApproximateReceiveCount": "1",
              "SentTimestamp": "1704106800000",
              "SenderId": "EXAMPLE123456789012",
              "ApproximateFirstReceiveTimestamp": "1704106800000"
            },
            "messageAttributes": {},
            "md5OfBody": "test-md5",
            "eventSource": "aws:sqs",
            "awsRegion": "eu-west-2"
          }
        ]
      }
      """
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
    Then there is 0 organisation, 0 location and 1 healthcare services created

    Then the 'healthcare-service' for service ID '56101471-f2b1-5324-83e2-1c6d55f3628c' has content:
      """
      {
        "id": "56101471-f2b1-5324-83e2-1c6d55f3628c",
        "field": "document",
        "active": true,
        "category": "GP Services",
        "createdBy": "DATA_MIGRATION",
        "ageEligibilityCriteria": null,
        "createdDateTime": "2025-10-07T08:38:57.679754Z",
        "dispositions": [],
        "identifier_oldDoS_uid": "2000094797",
        "location": null,
        "migrationNotes": [
          "field:['email'] ,error: not_nhs_email,message:Email address is not a valid NHS email address,value:178970-fake@nhs.gov.uk",
          "field:['publicphone'] ,error: empty,message:Phone number cannot be empty,value:None",
          "field:['nonpublicphone'] ,error: invalid_format,message:Phone number is invalid,value:99999000000"
        ],
        "modifiedBy": "DATA_MIGRATION",
        "modifiedDateTime": "2025-10-07T08:38:57.679754Z",
        "name": "PCN - Enhanced Access Hub, Sandwell",
        "openingTime": [],
        "providedBy": null,
        "symptomGroupSymptomDiscriminators": [],
        "telecom": {
          "email": null,
          "phone_private": null,
          "phone_public": null,
          "web": null
        },
        "type": "Primary Care Network Enhanced Access Service"
      }
      """
