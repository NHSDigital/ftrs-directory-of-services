@data-migration
Feature: Email Transformation

    Background:
        Given the test environment is configured
        And the DoS database has test data
        And DynamoDB tables are ready


    Scenario: Valid email address is transformed correctly
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                |
            | id                                  | 2101001                                              |
            | uid                                 | 210001                                               |
            | name                                | GP: Valid Email Surgery                              |
            | odscode                             | A23456                                               |
            | isnational                          |                                                      |
            | openallhours                        | false                                                |
            | publicreferralinstructions          |                                                      |
            | telephonetriagereferralinstructions | Valid email referral instructions                    |
            | restricttoreferrals                 | true                                                 |
            | address                             | Valid Surgery$10 Test Street$Test City$Test County   |
            | town                                | TEST CITY                                            |
            | postcode                            | TE1 1ST                                              |
            | easting                             | 400000                                               |
            | northing                            | 500000                                               |
            | publicphone                         | 01234567890                                          |
            | nonpublicphone                      | 01234567891                                          |
            | fax                                 | 01234567892                                          |
            | email                               | valid.email@nhs.net                                  |
            | web                                 | https://www.validemailsurgery.co.uk/                 |
            | createdby                           | HUMAN                                                |
            | createdtime                         | 2020-01-01 10:00:00.000                              |
            | modifiedby                          | ROBOT                                                |
            | modifiedtime                        | 2024-01-01 10:00:00.000                              |
            | lasttemplatename                    | Test Template                                        |
            | lasttemplateid                      | 100001                                               |
            | typeid                              | 100                                                  |
            | parentid                            | 1527                                                 |
            | subregionid                         | 1527                                                 |
            | statusid                            | 1                                                    |
            | organisationid                      |                                                      |
            | returnifopenminutes                 |                                                      |
            | publicname                          | Valid Email Surgery                                  |
            | latitude                            | 51.5074                                              |
            | longitude                           | -0.1278                                              |
            | professionalreferralinfo            |                                                      |
            | lastverified                        |                                                      |
            | nextverificationdue                 |                                                      |

        When the data migration process is run for table 'services', ID '2101001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id 'a16169ab-004c-5b51-803f-a621a064bfa2' has content:
            """
            {
                "migrationNotes": []
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id 'a16169ab-004c-5b51-803f-a621a064bfa2' has content:
            """
            {
                "telecom": {
                    "email": "valid.email@nhs.net",
                    "phone_private": "01234567891",
                    "phone_public": "01234567890",
                    "web": "https://www.validemailsurgery.co.uk/"
                }
            }
            """


    Scenario: Email with special characters is accepted
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                |
            | id                                  | 2102001                                              |
            | uid                                 | 210002                                               |
            | name                                | GP: Special Chars Email Surgery                      |
            | odscode                             | B23456                                               |
            | isnational                          |                                                      |
            | openallhours                        | false                                                |
            | publicreferralinstructions          |                                                      |
            | telephonetriagereferralinstructions | Special chars email referral instructions            |
            | restricttoreferrals                 | true                                                 |
            | address                             | Special Surgery$20 Test Street$Test City$Test County |
            | town                                | TEST CITY                                            |
            | postcode                            | TE2 2ST                                              |
            | easting                             | 400001                                               |
            | northing                            | 500001                                               |
            | publicphone                         | 01234567893                                          |
            | nonpublicphone                      | 01234567894                                          |
            | fax                                 | 01234567895                                          |
            | email                               | user.name+tag@subdomain.nhs.net                      |
            | web                                 | https://www.specialcharsemail.co.uk/                 |
            | createdby                           | HUMAN                                                |
            | createdtime                         | 2020-02-01 10:00:00.000                              |
            | modifiedby                          | ROBOT                                                |
            | modifiedtime                        | 2024-02-01 10:00:00.000                              |
            | lasttemplatename                    | Test Template 2                                      |
            | lasttemplateid                      | 100002                                               |
            | typeid                              | 100                                                  |
            | parentid                            | 1527                                                 |
            | subregionid                         | 1527                                                 |
            | statusid                            | 1                                                    |
            | organisationid                      |                                                      |
            | returnifopenminutes                 |                                                      |
            | publicname                          | Special Chars Email Surgery                          |
            | latitude                            | 51.5075                                              |
            | longitude                           | -0.1279                                              |
            | professionalreferralinfo            |                                                      |
            | lastverified                        |                                                      |
            | nextverificationdue                 |                                                      |

        When the data migration process is run for table 'services', ID '2102001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id 'f0e0264a-7cbd-5f1e-afda-ccc02da9aea3' has content:
            """
            {
                "migrationNotes": []
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id 'f0e0264a-7cbd-5f1e-afda-ccc02da9aea3' has content:
            """
            {
                "telecom": {
                    "email": "user.name+tag@subdomain.nhs.net",
                    "phone_private": "01234567894",
                    "phone_public": "01234567893",
                    "web": "https://www.specialcharsemail.co.uk/"
                }
            }
            """


    Scenario: Empty email triggers migration note
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                              |
            | id                                  | 2103001                                            |
            | uid                                 | 210003                                             |
            | name                                | GP: Empty Email Surgery                            |
            | odscode                             | C23456                                             |
            | isnational                          |                                                    |
            | openallhours                        | false                                              |
            | publicreferralinstructions          |                                                    |
            | telephonetriagereferralinstructions | Empty email referral instructions                  |
            | restricttoreferrals                 | true                                               |
            | address                             | Empty Surgery$30 Test Street$Test City$Test County |
            | town                                | TEST CITY                                          |
            | postcode                            | TE3 3ST                                            |
            | easting                             | 400002                                             |
            | northing                            | 500002                                             |
            | publicphone                         | 01234567896                                        |
            | nonpublicphone                      | 01234567897                                        |
            | fax                                 | 01234567898                                        |
            | email                               |                                                    |
            | web                                 | https://www.emptyemail.co.uk/                      |
            | createdby                           | HUMAN                                              |
            | createdtime                         | 2020-03-01 10:00:00.000                            |
            | modifiedby                          | ROBOT                                              |
            | modifiedtime                        | 2024-03-01 10:00:00.000                            |
            | lasttemplatename                    | Test Template 3                                    |
            | lasttemplateid                      | 100003                                             |
            | typeid                              | 100                                                |
            | parentid                            | 1527                                               |
            | subregionid                         | 1527                                               |
            | statusid                            | 1                                                  |
            | organisationid                      |                                                    |
            | returnifopenminutes                 |                                                    |
            | publicname                          | Empty Email Surgery                                |
            | latitude                            | 51.5076                                            |
            | longitude                           | -0.1280                                            |
            | professionalreferralinfo            |                                                    |
            | lastverified                        |                                                    |
            | nextverificationdue                 |                                                    |

        When the data migration process is run for table 'services', ID '2103001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id 'a4850070-e1c9-5359-9262-36f1bfe09720' has content:
            """
            {
                "migrationNotes": [
                    "field:['email'] ,error: email_not_string,message:Email must be a string,value:None"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id 'a4850070-e1c9-5359-9262-36f1bfe09720' has content:
            """
            {
                "telecom": {
                    "email": null,
                    "phone_private": "01234567897",
                    "phone_public": "01234567896",
                    "web": "https://www.emptyemail.co.uk/"
                }
            }
            """


    Scenario: Invalid email format is rejected
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                |
            | id                                  | 2104001                                              |
            | uid                                 | 210004                                               |
            | name                                | GP: Invalid Format Email Surgery                     |
            | odscode                             | D23456                                               |
            | isnational                          |                                                      |
            | openallhours                        | false                                                |
            | publicreferralinstructions          |                                                      |
            | telephonetriagereferralinstructions | Invalid format email referral instructions           |
            | restricttoreferrals                 | true                                                 |
            | address                             | Invalid Surgery$40 Test Street$Test City$Test County |
            | town                                | TEST CITY                                            |
            | postcode                            | TE4 4ST                                              |
            | easting                             | 400003                                               |
            | northing                            | 500003                                               |
            | publicphone                         | 01234567899                                          |
            | nonpublicphone                      | 01234567900                                          |
            | fax                                 | 01234567901                                          |
            | email                               | invalidemail                                         |
            | web                                 | https://www.invalidformat.co.uk/                     |
            | createdby                           | HUMAN                                                |
            | createdtime                         | 2020-04-01 10:00:00.000                              |
            | modifiedby                          | ROBOT                                                |
            | modifiedtime                        | 2024-04-01 10:00:00.000                              |
            | lasttemplatename                    | Test Template 4                                      |
            | lasttemplateid                      | 100004                                               |
            | typeid                              | 100                                                  |
            | parentid                            | 1527                                                 |
            | subregionid                         | 1527                                                 |
            | statusid                            | 1                                                    |
            | organisationid                      |                                                      |
            | returnifopenminutes                 |                                                      |
            | publicname                          | Invalid Format Email Surgery                         |
            | latitude                            | 51.5077                                              |
            | longitude                           | -0.1281                                              |
            | professionalreferralinfo            |                                                      |
            | lastverified                        |                                                      |
            | nextverificationdue                 |                                                      |

        When the data migration process is run for table 'services', ID '2104001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id 'ac76c7a6-bee8-5d22-bb87-7ddd8529d223' has content:
            """
            {
                "migrationNotes": [
                    "field:['email'] ,error: invalid_format,message:Email address is invalid,value:invalidemail"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id 'ac76c7a6-bee8-5d22-bb87-7ddd8529d223' has content:
            """
            {
                "telecom": {
                    "email": null,
                    "phone_private": "01234567900",
                    "phone_public": "01234567899",
                    "web": "https://www.invalidformat.co.uk/"
                }
            }
            """


    Scenario: Email with invalid structure is rejected
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                     |
            | id                                  | 2105001                                                   |
            | uid                                 | 210005                                                    |
            | name                                | GP: Invalid Structure Email Surgery                       |
            | odscode                             | E23456                                                    |
            | isnational                          |                                                           |
            | openallhours                        | false                                                     |
            | publicreferralinstructions          |                                                           |
            | telephonetriagereferralinstructions | Invalid structure email referral instructions             |
            | restricttoreferrals                 | true                                                      |
            | address                             | Invalid Surgery$50 Test Street$Test City$Test County      |
            | town                                | TEST CITY                                                 |
            | postcode                            | TE5 5ST                                                   |
            | easting                             | 400004                                                    |
            | northing                            | 500004                                                    |
            | publicphone                         | 01234567902                                               |
            | nonpublicphone                      | 01234567903                                               |
            | fax                                 | 01234567904                                               |
            | email                               | user name@nhs.net                                         |
            | web                                 | https://www.invalidstructure.co.uk/                       |
            | createdby                           | HUMAN                                                     |
            | createdtime                         | 2020-05-01 10:00:00.000                                   |
            | modifiedby                          | ROBOT                                                     |
            | modifiedtime                        | 2024-05-01 10:00:00.000                                   |
            | lasttemplatename                    | Test Template 5                                           |
            | lasttemplateid                      | 100005                                                    |
            | typeid                              | 100                                                       |
            | parentid                            | 1527                                                      |
            | subregionid                         | 1527                                                      |
            | statusid                            | 1                                                         |
            | organisationid                      |                                                           |
            | returnifopenminutes                 |                                                           |
            | publicname                          | Invalid Structure Email Surgery                           |
            | latitude                            | 51.5078                                                   |
            | longitude                           | -0.1282                                                   |
            | professionalreferralinfo            |                                                           |
            | lastverified                        |                                                           |
            | nextverificationdue                 |                                                           |

        When the data migration process is run for table 'services', ID '2105001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id 'cb1701c3-3fed-59ba-b6f4-a073eaef74f9' has content:
            """
            {
                "migrationNotes": [
                    "field:['email'] ,error: invalid_format,message:Email address is invalid,value:user name@nhs.net"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id 'cb1701c3-3fed-59ba-b6f4-a073eaef74f9' has content:
            """
            {
                "telecom": {
                    "email": null,
                    "phone_private": "01234567903",
                    "phone_public": "01234567902",
                    "web": "https://www.invalidstructure.co.uk/"
                }
            }
            """
