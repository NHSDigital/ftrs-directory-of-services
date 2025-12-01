@data-migration
Feature: Phone Transformation

    Background:
        Given the test environment is configured
        And the DoS database has test data
        And DynamoDB tables are ready

    Scenario: Valid phone numbers are transformed correctly
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                |
            | id                                  | 2001001                                              |
            | uid                                 | 200001                                               |
            | name                                | GP: Valid Phone Surgery                              |
            | odscode                             | A12345                                               |
            | isnational                          |                                                      |
            | openallhours                        | false                                                |
            | publicreferralinstructions          |                                                      |
            | telephonetriagereferralinstructions | Valid phone referral instructions                    |
            | restricttoreferrals                 | true                                                 |
            | address                             | Valid Surgery$10 Test Street$Test City$Test County   |
            | town                                | TEST CITY                                            |
            | postcode                            | TE1 1ST                                              |
            | easting                             | 400000                                               |
            | northing                            | 500000                                               |
            | publicphone                         | 01234567890                                          |
            | nonpublicphone                      | 01234567891                                          |
            | fax                                 | 01234567892                                          |
            | email                               | valid.phone@nhs.net                                  |
            | web                                 | https://www.validphonesurgery.co.uk/                 |
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
            | publicname                          | Valid Phone Surgery                                  |
            | latitude                            | 51.5074                                              |
            | longitude                           | -0.1278                                              |
            | professionalreferralinfo            |                                                      |
            | lastverified                        |                                                      |
            | nextverificationdue                 |                                                      |

        When the data migration process is run for table 'services', ID '2001001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id '0705993b-ffc5-54f9-9f3d-b1dad562233d' has content:
            """
            {
                "migrationNotes": []
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id '0705993b-ffc5-54f9-9f3d-b1dad562233d' has content:
            """
            {
                "telecom": {
                    "email": "valid.phone@nhs.net",
                    "phone_private": "01234567891",
                    "phone_public": "01234567890",
                    "web": "https://www.validphonesurgery.co.uk/"
                }
            }
            """


    Scenario: Invalid public phone number triggers migration note
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                |
            | id                                  | 2002001                                              |
            | uid                                 | 200002                                               |
            | name                                | GP: Invalid Public Phone Surgery                     |
            | odscode                             | B12345                                               |
            | isnational                          |                                                      |
            | openallhours                        | false                                                |
            | publicreferralinstructions          |                                                      |
            | telephonetriagereferralinstructions | Invalid phone referral instructions                  |
            | restricttoreferrals                 | true                                                 |
            | address                             | Invalid Surgery$20 Test Street$Test City$Test County |
            | town                                | TEST CITY                                            |
            | postcode                            | TE2 2ST                                              |
            | easting                             | 400001                                               |
            | northing                            | 500001                                               |
            | publicphone                         | INVALID123                                           |
            | nonpublicphone                      | 01234567893                                          |
            | fax                                 | 01234567894                                          |
            | email                               | invalid.public@nhs.net                               |
            | web                                 | https://www.invalidpublicphone.co.uk/                |
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
            | publicname                          | Invalid Public Phone Surgery                         |
            | latitude                            | 51.5075                                              |
            | longitude                           | -0.1279                                              |
            | professionalreferralinfo            |                                                      |
            | lastverified                        |                                                      |
            | nextverificationdue                 |                                                      |

        When the data migration process is run for table 'services', ID '2002001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id '1e6ed268-b391-5b8b-9046-ea47c1569097' has content:
            """
            {
                "migrationNotes": [
                    "field:['publicphone'] ,error: invalid_format,message:Phone number is invalid,value:INVALID123"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id '1e6ed268-b391-5b8b-9046-ea47c1569097' has content:
            """
            {
                "telecom": {
                    "email": "invalid.public@nhs.net",
                    "phone_private": "01234567893",
                    "phone_public": null,
                    "web": "https://www.invalidpublicphone.co.uk/"
                }
            }
            """

    Scenario: Invalid private phone number triggers migration note
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                  |
            | id                                  | 2003001                                                |
            | uid                                 | 200003                                                 |
            | name                                | GP: Invalid Private Phone Surgery                      |
            | odscode                             | C12345                                                 |
            | isnational                          |                                                        |
            | openallhours                        | false                                                  |
            | publicreferralinstructions          |                                                        |
            | telephonetriagereferralinstructions | Invalid private phone referral instructions            |
            | restricttoreferrals                 | true                                                   |
            | address                             | Invalid Surgery$30 Test Street$Test City$Test County   |
            | town                                | TEST CITY                                              |
            | postcode                            | TE3 3ST                                                |
            | easting                             | 400002                                                 |
            | northing                            | 500002                                                 |
            | publicphone                         | 01234567895                                            |
            | nonpublicphone                      | NOTANUMBER                                           |
            | fax                                 | 01234567896                                            |
            | email                               | invalid.private@nhs.net                                |
            | web                                 | https://www.invalidprivatephone.co.uk/                 |
            | createdby                           | HUMAN                                                  |
            | createdtime                         | 2020-03-01 10:00:00.000                                |
            | modifiedby                          | ROBOT                                                  |
            | modifiedtime                        | 2024-03-01 10:00:00.000                                |
            | lasttemplatename                    | Test Template 3                                        |
            | lasttemplateid                      | 100003                                                 |
            | typeid                              | 100                                                    |
            | parentid                            | 1527                                                   |
            | subregionid                         | 1527                                                   |
            | statusid                            | 1                                                      |
            | organisationid                      |                                                        |
            | returnifopenminutes                 |                                                        |
            | publicname                          | Invalid Private Phone Surgery                          |
            | latitude                            | 51.5076                                                |
            | longitude                           | -0.1280                                                |
            | professionalreferralinfo            |                                                        |
            | lastverified                        |                                                        |
            | nextverificationdue                 |                                                        |

        When the data migration process is run for table 'services', ID '2003001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id 'd8287566-3ed7-5c62-8398-5f61c725d3e1' has content:
            """
            {
                "migrationNotes": [
                    "field:['nonpublicphone'] ,error: invalid_format,message:Phone number is invalid,value:NOTANUMBER"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id 'd8287566-3ed7-5c62-8398-5f61c725d3e1' has content:
            """
            {
                "telecom": {
                    "email": "invalid.private@nhs.net",
                    "phone_private": null,
                    "phone_public": "01234567895",
                    "web": "https://www.invalidprivatephone.co.uk/"
                }
            }
            """


    Scenario: Empty phone numbers are handled correctly
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                              |
            | id                                  | 2004001                                            |
            | uid                                 | 200004                                             |
            | name                                | GP: Empty Phone Surgery                            |
            | odscode                             | D12345                                             |
            | isnational                          |                                                    |
            | openallhours                        | false                                              |
            | publicreferralinstructions          |                                                    |
            | telephonetriagereferralinstructions | Empty phone referral instructions                  |
            | restricttoreferrals                 | true                                               |
            | address                             | Empty Surgery$40 Test Street$Test City$Test County |
            | town                                | TEST CITY                                          |
            | postcode                            | TE4 4ST                                            |
            | easting                             | 400003                                             |
            | northing                            | 500003                                             |
            | publicphone                         |                                                    |
            | nonpublicphone                      |                                                    |
            | fax                                 | 01234567897                                        |
            | email                               | empty.phone@nhs.net                                |
            | web                                 | https://www.emptyphone.co.uk/                      |
            | createdby                           | HUMAN                                              |
            | createdtime                         | 2020-04-01 10:00:00.000                            |
            | modifiedby                          | ROBOT                                              |
            | modifiedtime                        | 2024-04-01 10:00:00.000                            |
            | lasttemplatename                    | Test Template 4                                    |
            | lasttemplateid                      | 100004                                             |
            | typeid                              | 100                                                |
            | parentid                            | 1527                                               |
            | subregionid                         | 1527                                               |
            | statusid                            | 1                                                  |
            | organisationid                      |                                                    |
            | returnifopenminutes                 |                                                    |
            | publicname                          | Empty Phone Surgery                                |
            | latitude                            | 51.5077                                            |
            | longitude                           | -0.1281                                            |
            | professionalreferralinfo            |                                                    |
            | lastverified                        |                                                    |
            | nextverificationdue                 |                                                    |

        When the data migration process is run for table 'services', ID '2004001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id 'd12e2794-2fda-555b-a39b-683ddbc07b0b' has content:
            """
            {
                "migrationNotes": [
                    "field:['publicphone'] ,error: empty,message:Phone number cannot be empty,value:None",
                    "field:['nonpublicphone'] ,error: empty,message:Phone number cannot be empty,value:None"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id 'd12e2794-2fda-555b-a39b-683ddbc07b0b' has content:
            """
            {
                "telecom": {
                    "email": "empty.phone@nhs.net",
                    "phone_private": null,
                    "phone_public": null,
                    "web": "https://www.emptyphone.co.uk/"
                }
            }
            """


    Scenario: Phone number with special characters is transformed
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                     |
            | id                                  | 2005001                                                   |
            | uid                                 | 200005                                                    |
            | name                                | GP: Special Chars Phone Surgery                           |
            | odscode                             | E12345                                                    |
            | isnational                          |                                                           |
            | openallhours                        | false                                                     |
            | publicreferralinstructions          |                                                           |
            | telephonetriagereferralinstructions | Special chars phone referral instructions                 |
            | restricttoreferrals                 | true                                                      |
            | address                             | Special Surgery$50 Test Street$Test City$Test County      |
            | town                                | TEST CITY                                                 |
            | postcode                            | TE5 5ST                                                   |
            | easting                             | 400004                                                    |
            | northing                            | 500004                                                    |
            | publicphone                         | 0123-456-7898                                             |
            | nonpublicphone                      | +44 1234 567899                                           |
            | fax                                 | 01234567900                                               |
            | email                               | special.chars@nhs.net                                     |
            | web                                 | https://www.specialchars.co.uk/                           |
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
            | publicname                          | Special Chars Phone Surgery                               |
            | latitude                            | 51.5078                                                   |
            | longitude                           | -0.1282                                                   |
            | professionalreferralinfo            |                                                           |
            | lastverified                        |                                                           |
            | nextverificationdue                 |                                                           |

        When the data migration process is run for table 'services', ID '2005001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id '7445f386-3efc-521f-8d26-04b5f749c873' has content:
            """
            {
                "migrationNotes": [
                    "field:['publicphone'] ,error: invalid_length,message:Phone number length is invalid,value:0123-456-7898"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id '7445f386-3efc-521f-8d26-04b5f749c873' has content:
            """
            {
                "telecom": {
                    "email": "special.chars@nhs.net",
                    "phone_private": "01234567899",
                    "phone_public": null,
                    "web": "https://www.specialchars.co.uk/"
                }
            }
            """


    Scenario: UK mobile number (07xxx) with only public phone
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                     |
            | id                                  | 2006001                                                   |
            | uid                                 | 200006                                                    |
            | name                                | GP: Mobile Phone Surgery                                  |
            | odscode                             | F12345                                                    |
            | isnational                          |                                                           |
            | openallhours                        | false                                                     |
            | publicreferralinstructions          |                                                           |
            | telephonetriagereferralinstructions | Mobile phone referral instructions                        |
            | restricttoreferrals                 | true                                                      |
            | address                             | Mobile Surgery$60 Test Street$Test City$Test County       |
            | town                                | TEST CITY                                                 |
            | postcode                            | TE6 6ST                                                   |
            | easting                             | 400005                                                    |
            | northing                            | 500005                                                    |
            | publicphone                         | 07700900123                                               |
            | nonpublicphone                      |                                                           |
            | fax                                 | 01234567901                                               |
            | email                               | mobile.phone@nhs.net                                      |
            | web                                 | https://www.mobilesurgery.co.uk/                          |
            | createdby                           | HUMAN                                                     |
            | createdtime                         | 2020-06-01 10:00:00.000                                   |
            | modifiedby                          | ROBOT                                                     |
            | modifiedtime                        | 2024-06-01 10:00:00.000                                   |
            | lasttemplatename                    | Test Template 6                                           |
            | lasttemplateid                      | 100006                                                    |
            | typeid                              | 100                                                       |
            | parentid                            | 1527                                                      |
            | subregionid                         | 1527                                                      |
            | statusid                            | 1                                                         |
            | organisationid                      |                                                           |
            | returnifopenminutes                 |                                                           |
            | publicname                          | Mobile Phone Surgery                                      |
            | latitude                            | 51.5079                                                   |
            | longitude                           | -0.1283                                                   |
            | professionalreferralinfo            |                                                           |
            | lastverified                        |                                                           |
            | nextverificationdue                 |                                                           |

        When the data migration process is run for table 'services', ID '2006001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id '345b19c4-a488-5315-a02e-331c35e99c53' has content:
            """
            {
                "migrationNotes": [
                    "field:['nonpublicphone'] ,error: empty,message:Phone number cannot be empty,value:None"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id '345b19c4-a488-5315-a02e-331c35e99c53' has content:
            """
            {
                "telecom": {
                    "email": "mobile.phone@nhs.net",
                    "phone_private": null,
                    "phone_public": "07700900123",
                    "web": "https://www.mobilesurgery.co.uk/"
                }
            }
            """


    Scenario: International format (+44) with only private phone
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                     |
            | id                                  | 2007001                                                   |
            | uid                                 | 200007                                                    |
            | name                                | GP: International Phone Surgery                           |
            | odscode                             | G12345                                                    |
            | isnational                          |                                                           |
            | openallhours                        | false                                                     |
            | publicreferralinstructions          |                                                           |
            | telephonetriagereferralinstructions | International phone referral instructions                 |
            | restricttoreferrals                 | true                                                      |
            | address                             | International Surgery$70 Test Street$Test City$Test County |
            | town                                | TEST CITY                                                 |
            | postcode                            | TE7 7ST                                                   |
            | easting                             | 400006                                                    |
            | northing                            | 500006                                                    |
            | publicphone                         |                                                           |
            | nonpublicphone                      | +447812345678                                             |
            | fax                                 | 01234567902                                               |
            | email                               | international.phone@nhs.net                               |
            | web                                 | https://www.internationalsurgery.co.uk/                   |
            | createdby                           | HUMAN                                                     |
            | createdtime                         | 2020-07-01 10:00:00.000                                   |
            | modifiedby                          | ROBOT                                                     |
            | modifiedtime                        | 2024-07-01 10:00:00.000                                   |
            | lasttemplatename                    | Test Template 7                                           |
            | lasttemplateid                      | 100007                                                    |
            | typeid                              | 100                                                       |
            | parentid                            | 1527                                                      |
            | subregionid                         | 1527                                                      |
            | statusid                            | 1                                                         |
            | organisationid                      |                                                           |
            | returnifopenminutes                 |                                                           |
            | publicname                          | International Phone Surgery                               |
            | latitude                            | 51.5080                                                   |
            | longitude                           | -0.1284                                                   |
            | professionalreferralinfo            |                                                           |
            | lastverified                        |                                                           |
            | nextverificationdue                 |                                                           |

        When the data migration process is run for table 'services', ID '2007001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id 'd060506c-e543-5022-91b9-fd83aa9d6cdf' has content:
            """
            {
                "migrationNotes": [
                    "field:['publicphone'] ,error: empty,message:Phone number cannot be empty,value:None"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id 'd060506c-e543-5022-91b9-fd83aa9d6cdf' has content:
            """
            {
                "telecom": {
                    "email": "international.phone@nhs.net",
                    "phone_private": "07812345678",
                    "phone_public": null,
                    "web": "https://www.internationalsurgery.co.uk/"
                }
            }
            """


    Scenario: Both phones too short are rejected
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                     |
            | id                                  | 2008001                                                   |
            | uid                                 | 200008                                                    |
            | name                                | GP: Too Short Phone Surgery                               |
            | odscode                             | H12345                                                    |
            | isnational                          |                                                           |
            | openallhours                        | false                                                     |
            | publicreferralinstructions          |                                                           |
            | telephonetriagereferralinstructions | Too short phone referral instructions                     |
            | restricttoreferrals                 | true                                                      |
            | address                             | Short Surgery$80 Test Street$Test City$Test County        |
            | town                                | TEST CITY                                                 |
            | postcode                            | TE8 8ST                                                   |
            | easting                             | 400007                                                    |
            | northing                            | 500007                                                    |
            | publicphone                         | 012345678                                                 |
            | nonpublicphone                      | 0123456                                                   |
            | fax                                 | 01234567903                                               |
            | email                               | tooshort.phone@nhs.net                                    |
            | web                                 | https://www.tooshortsurgery.co.uk/                        |
            | createdby                           | HUMAN                                                     |
            | createdtime                         | 2020-08-01 10:00:00.000                                   |
            | modifiedby                          | ROBOT                                                     |
            | modifiedtime                        | 2024-08-01 10:00:00.000                                   |
            | lasttemplatename                    | Test Template 8                                           |
            | lasttemplateid                      | 100008                                                    |
            | typeid                              | 100                                                       |
            | parentid                            | 1527                                                      |
            | subregionid                         | 1527                                                      |
            | statusid                            | 1                                                         |
            | organisationid                      |                                                           |
            | returnifopenminutes                 |                                                           |
            | publicname                          | Too Short Phone Surgery                                   |
            | latitude                            | 51.5081                                                   |
            | longitude                           | -0.1285                                                   |
            | professionalreferralinfo            |                                                           |
            | lastverified                        |                                                           |
            | nextverificationdue                 |                                                           |

        When the data migration process is run for table 'services', ID '2008001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id '41ea2514-9e95-579a-8dfa-54d11a0548fb' has content:
            """
            {
                "migrationNotes": [
                    "field:['publicphone'] ,error: invalid_length,message:Phone number length is invalid,value:012345678",
                    "field:['nonpublicphone'] ,error: invalid_length,message:Phone number length is invalid,value:0123456"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id '41ea2514-9e95-579a-8dfa-54d11a0548fb' has content:
            """
            {
                "telecom": {
                    "email": "tooshort.phone@nhs.net",
                    "phone_private": null,
                    "phone_public": null,
                    "web": "https://www.tooshortsurgery.co.uk/"
                }
            }
            """


    Scenario: Private phone too long is rejected, public phone valid
        Given a "Service" exists in DoS with attributes
            | key                                 | value                                                     |
            | id                                  | 2009001                                                   |
            | uid                                 | 200009                                                    |
            | name                                | GP: Too Long Phone Surgery                                |
            | odscode                             | J12345                                                    |
            | isnational                          |                                                           |
            | openallhours                        | false                                                     |
            | publicreferralinstructions          |                                                           |
            | telephonetriagereferralinstructions | Too long phone referral instructions                      |
            | restricttoreferrals                 | true                                                      |
            | address                             | Long Surgery$90 Test Street$Test City$Test County         |
            | town                                | TEST CITY                                                 |
            | postcode                            | TE9 9ST                                                   |
            | easting                             | 400008                                                    |
            | northing                            | 500008                                                    |
            | publicphone                         | 01234567890                                               |
            | nonpublicphone                      | 01234567890123                                            |
            | fax                                 | 01234567904                                               |
            | email                               | toolong.phone@nhs.net                                     |
            | web                                 | https://www.toolongsurgery.co.uk/                         |
            | createdby                           | HUMAN                                                     |
            | createdtime                         | 2020-09-01 10:00:00.000                                   |
            | modifiedby                          | ROBOT                                                     |
            | modifiedtime                        | 2024-09-01 10:00:00.000                                   |
            | lasttemplatename                    | Test Template 9                                           |
            | lasttemplateid                      | 100009                                                    |
            | typeid                              | 100                                                       |
            | parentid                            | 1527                                                      |
            | subregionid                         | 1527                                                      |
            | statusid                            | 1                                                         |
            | organisationid                      |                                                           |
            | returnifopenminutes                 |                                                           |
            | publicname                          | Too Long Phone Surgery                                    |
            | latitude                            | 51.5082                                                   |
            | longitude                           | -0.1286                                                   |
            | professionalreferralinfo            |                                                           |
            | lastverified                        |                                                           |
            | nextverificationdue                 |                                                           |

        When the data migration process is run for table 'services', ID '2009001' and method 'insert'
        Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
        Then there is 1 organisation, 1 location and 1 healthcare services created
        Then field 'migrationNotes' on table 'healthcare-service' for id 'c28fe5ec-ee88-5541-908b-d73a91afcd54' has content:
            """
            {
                "migrationNotes": [
                    "field:['nonpublicphone'] ,error: invalid_length,message:Phone number length is invalid,value:01234567890123"
                ]
            }
            """
        Then field 'telecom' on table 'healthcare-service' for id 'c28fe5ec-ee88-5541-908b-d73a91afcd54' has content:
            """
            {
                "telecom": {
                    "email": "toolong.phone@nhs.net",
                    "phone_private": null,
                    "phone_public": "01234567890",
                    "web": "https://www.toolongsurgery.co.uk/"
                }
            }
            """
