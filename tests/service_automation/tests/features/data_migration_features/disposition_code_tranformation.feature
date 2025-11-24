@data-migration
Feature: Data Migration

    Background:
        Given the test environment is configured
        And the DoS database has test data
        And DynamoDB tables are ready

    Scenario: Multiple disposition codes are transformed
         Given a 'Service' exists called 'Redlam Surgery' in DoS with attributes:
            | key                                 | value                                                       |
            | id                                  | 6001533                                                     |
            | uid                                 | 113474                                                      |
            | name                                | GP: Redlam Surgery - Blackburn                              |
            | odscode                             | P81061                                                      |
            | isnational                          |                                                             |
            | openallhours                        | false                                                       |
            | publicreferralinstructions          |                                                             |
            | telephonetriagereferralinstructions | STUB Telephone Triage Referral Instructions Text Field 1533 |
            | restricttoreferrals                 | true                                                        |
            | address                             | Redlam Surgery$62-64 Redlam$Blackburn$Lancashire            |
            | town                                | BLACKBURN                                                   |
            | postcode                            | BB2 1UW                                                     |
            | easting                             | 366856                                                      |
            | northing                            | 427476                                                      |
            | publicphone                         | 01254260051                                                 |
            | nonpublicphone                      |                                                             |
            | fax                                 | 00000 666666                                                |
            | email                               | 1533-fake@nhs.gov.uk                                        |
            | web                                 | https://www.redlamsurgery.co.uk/                            |
            | createdby                           | HUMAN                                                       |
            | createdtime                         | 2011-06-17 09:19:36.000                                     |
            | modifiedby                          | ROBOT                                                       |
            | modifiedtime                        | 2025-02-11 16:32:18.000                                     |
            | lasttemplatename                    | BwD GP Update 08 01 25                                      |
            | lasttemplateid                      | 245697                                                      |
            | typeid                              | 100                                                         |
            | parentid                            | 1527                                                        |
            | subregionid                         | 1527                                                        |
            | statusid                            | 1                                                           |
            | organisationid                      |                                                             |
            | returnifopenminutes                 |                                                             |
            | publicname                          | Redlam Surgery - Blackburn                                  |
            | latitude                            | 53.7426167                                                  |
            | longitude                           | -2.5039993                                                  |
            | professionalreferralinfo            |                                                             |
            | lastverified                        |                                                             |
            | nextverificationdue                 |                                                             |

        Given a 'ServiceDisposition' exists called 'Redlam Surgery' in DoS with attributes:
            | key           | value     |
            | id            | 61007338 |
            | serviceid      | 6001533   |
            | dispositionid | 4         |

        Given a 'ServiceDisposition' exists called 'Redlam Surgery' in DoS with attributes:
            | key           | value      |
            | id            | 62007338 |
            | serviceid      | 6001533    |
            | dispositionid | 5          |

        When the data migration process is run with the event:
            """
            {
                "Records": [
                    {
                        "messageId": "test-message-1",
                        "receiptHandle": "test-receipt-handle",
                        "body": "{\"type\": \"dms_event\", \"record_id\": 6001533, \"table_name\": \"services\", \"method\": \"insert\"}",
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
        Then there is 1 organisation, 1 location and 1 healthcare services created

        Then the 'healthcare-service' for service ID '6fa132cc-0096-5665-ada1-76e23823ac4c' has content:
            """
            {
                "id": "6fa132cc-0096-5665-ada1-76e23823ac4c",
                "field": "document",
                "active": true,
                "ageEligibilityCriteria": [],
                "category": "GP Services",
                "createdBy": "DATA_MIGRATION",
                "createdDateTime": "2025-11-14T14:31:54.666870Z",
                "dispositions": [
                    {
                        "id": "932b524f-4d66-50be-b34d-f1ab5afe413c",
                        "codeID": 4,
                        "codeType": "Disposition (Dx)",
                        "codeValue": "To contact a Primary Care Service within 2 hours",
                        "source": "pathways",
                        "time": 120
                    },
                    {
                        "id": "2730f66b-5f48-5585-a9c2-aac79ab97081",
                        "codeID": 5,
                        "codeType": "Disposition (Dx)",
                        "codeValue": "To contact a Primary Care Service within 6 hours",
                        "source": "pathways",
                        "time": 360
                    }
                ],
                "identifier_oldDoS_uid": "113474",
                "location": "46db3afc-65a4-5148-b804-892313fb1ed7",
                "migrationNotes": [
                    "field:['email'] ,error: not_nhs_email,message:Email address is not a valid NHS email address,value:1533-fake@nhs.gov.uk",
                    "field:['nonpublicphone'] ,error: empty,message:Phone number cannot be empty,value:None"
                ],
                "modifiedBy": "DATA_MIGRATION",
                "modifiedDateTime": "2025-11-14T14:31:54.666870Z",
                "name": "GP: Redlam Surgery - Blackburn",
                "openingTime": [],
                "providedBy": "775d05bf-93df-5d9e-9906-e30e663ac552",
                "symptomGroupSymptomDiscriminators": [],
                "telecom": {
                    "email": null,
                    "phone_private": null,
                    "phone_public": "01254260051",
                    "web": "https://www.redlamsurgery.co.uk/"
                },
                "type": "GP Consultation Service"
            }
            """
