@data-migration
Feature: Data Migration

    Background:
        Given the test environment is configured
        And the DoS database has test data
        And DynamoDB tables are ready

    Scenario: Multiple consecutive date ranges are transformed
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                       |
            | id                                  | 1001533                                                     |
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

        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 1007338 |
            | daysfrom  | 5844.0  |
            | daysto    | 47481.5 |
            | serviceid | 1001533 |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value    |
            | id        | 1007339  |
            | daysfrom  | 23741.25 |
            | daysto    | 47481.5  |
            | serviceid | 1001533  |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 1007340 |
            | daysfrom  | 365.25  |
            | daysto    | 1825.25 |
            | serviceid | 1001533 |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 1007341 |
            | daysfrom  | 1826.25 |
            | daysto    | 5843.0  |
            | serviceid | 1001533 |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 1007342 |
            | daysfrom  | 0.0     |
            | daysto    | 364.25  |
            | serviceid | 1001533 |

        When the data migration process is run for table 'services', ID '1001533' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created

        Then the 'healthcare-service' for service ID '1001533' has content:
            """
            {
                "id": "3a3bab5d-6931-5e79-96af-e723aa87b078",
                "field": "document",
                "active": true,
                "ageEligibilityCriteria": [
                    {
                        "rangeFrom": "0",
                        "rangeTo": "47481.5",
                        "type": "days"
                    }
                ],
                "category": "GP Services",
                "createdBy": "DATA_MIGRATION",
                "createdDateTime": "2025-11-14T14:31:54.666870Z",
                "dispositions": [],
                "identifier_oldDoS_uid": "113474",
                "location": "3f0ded02-8e5f-5be7-a3dd-5c201314ac7e",
                "migrationNotes": [
                    "field:['email'] ,error: not_nhs_email,message:Email address is not a valid NHS email address,value:1533-fake@nhs.gov.uk",
                    "field:['nonpublicphone'] ,error: empty,message:Phone number cannot be empty,value:None"
                ],
                "modifiedBy": "DATA_MIGRATION",
                "modifiedDateTime": "2025-11-14T14:31:54.666870Z",
                "name": "GP: Redlam Surgery - Blackburn",
                "openingTime": [],
                "providedBy": "7fb0593f-bdad-5a6c-bbe8-760da76ab0d9",
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


    Scenario: Multiple non-consecutive date ranges are transformed
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                       |
            | id                                  | 2001533                                                     |
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

        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 2007338 |
            | daysfrom  | 5844.0  |
            | daysto    | 47481.5 |
            | serviceid | 2001533 |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value    |
            | id        | 2007339  |
            | daysfrom  | 23741.25 |
            | daysto    | 47481.5  |
            | serviceid | 2001533  |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 2007341 |
            | daysfrom  | 1826.25 |
            | daysto    | 5843.0  |
            | serviceid | 2001533 |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 2007342 |
            | daysfrom  | 0.0     |
            | daysto    | 364.25  |
            | serviceid | 2001533 |

        When the data migration process is run for table 'services', ID '2001533' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created

        Then the 'healthcare-service' for service ID '2001533' has content:
            """
            {
                "id": "7194eaa7-8f8e-57e2-a8ac-b694aba132cf",
                "field": "document",
                "active": true,
                "ageEligibilityCriteria": [
                    {
                        "rangeFrom": "0",
                        "rangeTo": "364.25",
                        "type": "days"
                    },
                    {
                        "rangeFrom": "1826.25",
                        "rangeTo": "47481.5",
                        "type": "days"
                    }
                ],
                "category": "GP Services",
                "createdBy": "DATA_MIGRATION",
                "createdDateTime": "2025-11-14T14:31:54.666870Z",
                "dispositions": [],
                "identifier_oldDoS_uid": "113474",
                "location": "59e9ec2a-63d0-551f-ba1e-a0e34befae1a",
                "migrationNotes": [
                    "field:['email'] ,error: not_nhs_email,message:Email address is not a valid NHS email address,value:1533-fake@nhs.gov.uk",
                    "field:['nonpublicphone'] ,error: empty,message:Phone number cannot be empty,value:None"
                ],
                "modifiedBy": "DATA_MIGRATION",
                "modifiedDateTime": "2025-11-14T14:31:54.666870Z",
                "name": "GP: Redlam Surgery - Blackburn",
                "openingTime": [],
                "providedBy": "1693c0c9-d295-5f0d-83ac-152eaa8d4ea7",
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



    Scenario: Negative "days from" in age range is accepted as a valid value
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                       |
            | id                                  | 3001533                                                     |
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

        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 3007338 |
            | daysfrom  | -5844.0 |
            | daysto    | 47481.5 |
            | serviceid | 3001533 |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 3007339 |
            | daysfrom  | 0       |
            | daysto    | 37481.5 |
            | serviceid | 3001533 |

        When the data migration process is run for table 'services', ID '3001533' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then the 'healthcare-service' for service ID '3001533' has content:
            """
            {
                "id": "8d73a7f5-1e60-5880-902f-4ad5d4b9f08b",
                "field": "document",
                "active": true,
                "ageEligibilityCriteria": [
                    {
                        "rangeFrom": "-5844",
                        "rangeTo": "47481.5",
                        "type": "days"
                    }
                ],
                "category": "GP Services",
                "createdBy": "DATA_MIGRATION",
                "createdDateTime": "2025-11-14T14:31:54.666870Z",
                "dispositions": [],
                "identifier_oldDoS_uid": "113474",
                "location": "40c28a0e-0262-5044-8fc2-264accef328b",
                "migrationNotes": [
                    "field:['email'] ,error: not_nhs_email,message:Email address is not a valid NHS email address,value:1533-fake@nhs.gov.uk",
                    "field:['nonpublicphone'] ,error: empty,message:Phone number cannot be empty,value:None"
                ],
                "modifiedBy": "DATA_MIGRATION",
                "modifiedDateTime": "2025-11-14T14:31:54.666870Z",
                "name": "GP: Redlam Surgery - Blackburn",
                "openingTime": [],
                "providedBy": "b40daca7-4269-5b64-ad46-8c0857c505f9",
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

    Scenario: Negative "days to" in age range is accepted as a valid value
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                       |
            | id                                  | 4001533                                                     |
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

        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 4007338 |
            | daysfrom  | 5844.0  |
            | daysto    | 47481.5 |
            | serviceid | 4001533 |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value    |
            | id        | 4007339  |
            | daysfrom  | 23741.25 |
            | daysto    | -47481.5 |
            | serviceid | 4001533  |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 4007341 |
            | daysfrom  | 1826.25 |
            | daysto    | 5843.0  |
            | serviceid | 4001533 |
        Given a "ServiceAgeRange" exists in DoS with attributes
            | key       | value   |
            | id        | 4007342 |
            | daysfrom  | 0.0     |
            | daysto    | 364.25  |
            | serviceid | 4001533 |

        When the data migration process is run for table 'services', ID '4001533' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created

        Then the 'healthcare-service' for service ID '4001533' has content:
            """
            {
                "id": "be4d2882-bfaf-521c-b3fe-7d6bd8c9142b",
                "field": "document",
                "active": true,
                "ageEligibilityCriteria": [
                    {
                        "rangeFrom": "0",
                        "rangeTo": "364.25",
                        "type": "days"
                    },
                    {
                        "rangeFrom": "1826.25",
                        "rangeTo": "47481.5",
                        "type": "days"
                    }
                ],
                "category": "GP Services",
                "createdBy": "DATA_MIGRATION",
                "createdDateTime": "2025-11-14T14:31:54.666870Z",
                "dispositions": [],
                "identifier_oldDoS_uid": "113474",
                "location": "5701852c-4ff9-5c6e-b541-a029ab30e25b",
                "migrationNotes": [
                    "field:['email'] ,error: not_nhs_email,message:Email address is not a valid NHS email address,value:1533-fake@nhs.gov.uk",
                    "field:['nonpublicphone'] ,error: empty,message:Phone number cannot be empty,value:None"
                ],
                "modifiedBy": "DATA_MIGRATION",
                "modifiedDateTime": "2025-11-14T14:31:54.666870Z",
                "name": "GP: Redlam Surgery - Blackburn",
                "openingTime": [],
                "providedBy": "41348f64-c784-507e-846b-62717a70a9c9",
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
