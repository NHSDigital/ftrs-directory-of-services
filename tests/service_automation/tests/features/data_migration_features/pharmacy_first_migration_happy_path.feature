@data-migration
Feature: Data Migration - Pharmacy First

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  @happy
  Scenario: Pharmacy First (M06) migration when parent Community Pharmacy has not been migrated yet
    # Parent Community Pharmacy (type 13) with ODS code FV498 exists in DoS but has NOT been migrated.
    # When the PF++ service (ODS FV498M06) is processed, the processor auto-migrates the parent first
    # (transaction 1), then creates the Pharmacy First HealthcareService linked to the parent
    # org/location (transaction 2).
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 214258                                                  |
      | uid                                 | 2000130082                                              |
      | name                                | Boots - Folkestone                                      |
      | odscode                             | FV498                                                   |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 22 Sandgate Road$Folkestone$Kent                        |
      | town                                | FOLKESTONE                                              |
      | postcode                            | CT20 1DR                                                |
      | easting                             | 621000                                                  |
      | northing                            | 136000                                                  |
      | publicphone                         | 01303123456                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 214258-fake@nhs.gov.uk                                  |
      | web                                 | www.boots.com                                           |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2023-10-24 11:36:40.000                                 |
      | modifiedby                          | HUMAN                                                   |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                 |
      | lasttemplatename                    | Pharmacy Template                                       |
      | lasttemplateid                      | 221808                                                  |
      | typeid                              | 13                                                      |
      | parentid                            | 196814                                                  |
      | subregionid                         | 150021                                                  |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Boots                                                   |
      | latitude                            | 51.0828000                                              |
      | longitude                           | 1.1780000                                               |
      | professionalreferralinfo            |                                                         |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |
    And a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 214259                                                  |
      | uid                                 | 2000130083                                              |
      | name                                | PF++: Kent - Boots - Folkestone                         |
      | odscode                             | FV498M06                                                |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 22 Sandgate Road$Folkestone$Kent                        |
      | town                                | FOLKESTONE                                              |
      | postcode                            | CT20 1DR                                                |
      | easting                             | 621000                                                  |
      | northing                            | 136000                                                  |
      | publicphone                         | 01303123456                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 214259-fake@nhs.gov.uk                                  |
      | web                                 | www.boots.com                                           |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2023-10-24 11:36:40.000                                 |
      | modifiedby                          | HUMAN                                                   |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                 |
      | lasttemplatename                    | *Service* Template - NHS Pharmacy First (PF++) R1.0     |
      | lasttemplateid                      | 221811                                                  |
      | typeid                              | 132                                                     |
      | parentid                            | 196814                                                  |
      | subregionid                         | 150021                                                  |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Boots                                                   |
      | latitude                            | 51.0828000                                              |
      | longitude                           | 1.1780000                                               |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |

    When the data migration process is run for table 'services', ID '214259' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 2 healthcare services created
    And the state table contains a record for key 'services#214259' with version 1

    # Validate that the Pharmacy First healthcare service is linked to the auto-migrated parent org/location
    Then the 'healthcare-service' for service ID '214259' has content:
      """
      {
        "id": "91103641-dc4a-5428-8241-ab10ba6eb485",
        "identifier_oldDoS_uid": "2000130083",
        "providedBy": "eac08862-442a-5db6-9bd7-b7c855ba3540",
        "location": "6f4f3e6c-ba93-51e4-ad5e-8a7255ae204a",
        "name": "PF++: Kent - Boots - Folkestone",
        "category": "Pharmacy Services",
        "type": "Pharmacy First",
        "status": "active"
      }
      """

  @happy
  Scenario: Pharmacy First (M06DSP) migration when parent Distance Selling Pharmacy has not been migrated yet
    # Parent Distance Selling Pharmacy (type 134) with ODS code FV499 exists in DoS but has NOT been migrated.
    # When the PF++ service (ODS FV499M06DSP) is processed, the processor auto-migrates the parent first
    # (transaction 1), then creates the Pharmacy First HealthcareService linked to the parent
    # org/location (transaction 2).
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 214260                                                  |
      | uid                                 | 2000130084                                              |
      | name                                | Online Pharmacy - Dover                                 |
      | odscode                             | FV499                                                   |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 1 Castle Street$Dover$Kent                              |
      | town                                | DOVER                                                   |
      | postcode                            | CT16 1PJ                                                |
      | easting                             | 632000                                                  |
      | northing                            | 141000                                                  |
      | publicphone                         | 01304987654                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 214260-fake@nhs.gov.uk                                  |
      | web                                 | www.onlinepharmacy.com                                  |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2023-10-24 11:36:40.000                                 |
      | modifiedby                          | HUMAN                                                   |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                 |
      | lasttemplatename                    | Pharmacy Distance Selling Template                      |
      | lasttemplateid                      | 221812                                                  |
      | typeid                              | 134                                                     |
      | parentid                            | 196814                                                  |
      | subregionid                         | 150021                                                  |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Online Pharmacy                                         |
      | latitude                            | 51.1270000                                              |
      | longitude                           | 1.3090000                                               |
      | professionalreferralinfo            |                                                         |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |
    And a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 214261                                                  |
      | uid                                 | 2000130085                                              |
      | name                                | PF++: Kent - Online Pharmacy - Dover                    |
      | odscode                             | FV499M06DSP                                             |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 1 Castle Street$Dover$Kent                              |
      | town                                | DOVER                                                   |
      | postcode                            | CT16 1PJ                                                |
      | easting                             | 632000                                                  |
      | northing                            | 141000                                                  |
      | publicphone                         | 01304987654                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 214261-fake@nhs.gov.uk                                  |
      | web                                 | www.onlinepharmacy.com                                  |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2023-10-24 11:36:40.000                                 |
      | modifiedby                          | HUMAN                                                   |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                 |
      | lasttemplatename                    | *Service* Template - NHS Pharmacy First (PF++) R1.0     |
      | lasttemplateid                      | 221811                                                  |
      | typeid                              | 132                                                     |
      | parentid                            | 196814                                                  |
      | subregionid                         | 150021                                                  |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Online Pharmacy                                         |
      | latitude                            | 51.1270000                                              |
      | longitude                           | 1.3090000                                               |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |

    When the data migration process is run for table 'services', ID '214261' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 2 healthcare services created
    And the state table contains a record for key 'services#214261' with version 1

    # Validate that the Pharmacy First healthcare service is linked to the auto-migrated parent org/location
    Then the 'healthcare-service' for service ID '214261' has content:
      """
      {
        "id": "b88680b0-b7f9-527e-9a0d-a54e556b6b02",
        "identifier_oldDoS_uid": "2000130085",
        "providedBy": "d349e0bc-a8ef-50cd-972b-93ef215bd539",
        "location": "70229df2-984d-598c-877d-12c8ca999a92",
        "name": "PF++: Kent - Online Pharmacy - Dover",
        "category": "Pharmacy Services",
        "type": "Pharmacy First",
        "status": "active"
      }
      """

  @happy
  Scenario: Pharmacy First (M06) migration when parent Community Pharmacy is already migrated
    # Parent Community Pharmacy (type 13) with ODS code FV500 is migrated first, establishing its
    # org/location in state. When the PF++ service (ODS FV500M06) is processed, the processor
    # reuses the existing parent org/location IDs directly from the state table — no second
    # parent migration occurs.
    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 214262                                                  |
      | uid                                 | 2000130086                                              |
      | name                                | Boots - Ashford                                         |
      | odscode                             | FV500                                                   |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 5 Bank Street$Ashford$Kent                              |
      | town                                | ASHFORD                                                 |
      | postcode                            | TN23 1DA                                                |
      | easting                             | 601000                                                  |
      | northing                            | 142000                                                  |
      | publicphone                         | 01233111222                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 214262-fake@nhs.gov.uk                                  |
      | web                                 | www.boots.com                                           |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2023-10-24 11:36:40.000                                 |
      | modifiedby                          | HUMAN                                                   |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                 |
      | lasttemplatename                    | Pharmacy Template                                       |
      | lasttemplateid                      | 221808                                                  |
      | typeid                              | 13                                                      |
      | parentid                            | 196814                                                  |
      | subregionid                         | 150021                                                  |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Boots                                                   |
      | latitude                            | 51.1460000                                              |
      | longitude                           | 0.8740000                                               |
      | professionalreferralinfo            |                                                         |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |

    # Migrate the parent pharmacy first so its state record and org/location exist in DynamoDB
    When the data migration process is run for table 'services', ID '214262' and method 'insert'

    Given a "Service" exists in DoS with attributes
      | key                                 | value                                                   |
      | id                                  | 214263                                                  |
      | uid                                 | 2000130087                                              |
      | name                                | PF++: Kent - Boots - Ashford                            |
      | odscode                             | FV500M06                                                |
      | openallhours                        | FALSE                                                   |
      | publicreferralinstructions          |                                                         |
      | telephonetriagereferralinstructions |                                                         |
      | restricttoreferrals                 | FALSE                                                   |
      | address                             | 5 Bank Street$Ashford$Kent                              |
      | town                                | ASHFORD                                                 |
      | postcode                            | TN23 1DA                                                |
      | easting                             | 601000                                                  |
      | northing                            | 142000                                                  |
      | publicphone                         | 01233111222                                             |
      | nonpublicphone                      |                                                         |
      | fax                                 |                                                         |
      | email                               | 214263-fake@nhs.gov.uk                                  |
      | web                                 | www.boots.com                                           |
      | createdby                           | HUMAN                                                   |
      | createdtime                         | 2023-10-24 11:36:40.000                                 |
      | modifiedby                          | HUMAN                                                   |
      | modifiedtime                        | 2025-01-02 07:09:38.000                                 |
      | lasttemplatename                    | *Service* Template - NHS Pharmacy First (PF++) R1.0     |
      | lasttemplateid                      | 221811                                                  |
      | typeid                              | 132                                                     |
      | parentid                            | 196814                                                  |
      | subregionid                         | 150021                                                  |
      | statusid                            | 1                                                       |
      | organisationid                      |                                                         |
      | returnifopenminutes                 |                                                         |
      | publicname                          | Boots                                                   |
      | latitude                            | 51.1460000                                              |
      | longitude                           | 0.8740000                                               |
      | professionalreferralinfo            | This is a self referral service. Advise the patient to make their way to the pharmacy. |
      | lastverified                        |                                                         |
      | nextverificationdue                 |                                                         |

    When the data migration process is run for table 'services', ID '214263' and method 'insert'
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 inserted, 0 updated, 0 skipped and 0 errors
    And there is 1 organisation, 1 location and 2 healthcare services created
    And the state table contains a record for key 'services#214263' with version 1

    # Validate the PF++ service is linked to the already-migrated parent org/location
    Then the 'healthcare-service' for service ID '214263' has content:
      """
      {
        "id": "40145796-932b-50b8-91c7-d1b3159499bc",
        "identifier_oldDoS_uid": "2000130087",
        "providedBy": "0ebb1699-c3af-5d86-b643-e200ca756361",
        "location": "3ad1f07f-82df-5eaf-bebf-2f06172ecab5",
        "name": "PF++: Kent - Boots - Ashford",
        "category": "Pharmacy Services",
        "type": "Pharmacy First",
        "status": "active"
      }
      """
