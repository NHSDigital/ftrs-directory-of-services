@data-migration
Feature: Service Transformation with Invalid Address Combinations

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario Outline: Migrate GP practice with various address field combinations
    Given a 'Service' exists called '<service_name>' in DoS with attributes:
      | key                 | value                                      |
      | id                  | <service_id>                               |
      | uid                 | <uid>                                      |
      | name                | <service_name>                             |
      | publicname          | <public_name>                              |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | <ods_code>                                 |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            | <postcode>                                 |
      | address             | <address>                                  |
      | town                | <town>                                     |
      | web                 | https://www.nhs.uk/                        |
      | email               | england.contactus@nhs.net                  |
      | publicphone         | 0300 311 22 33                             |
    When a single service migration is run for ID '<service_id>'
    Then the metrics should be 1 total, <expected_supported> supported, <expected_unsupported> unsupported, <expected_transformed> transformed, <expected_migrated> migrated, <expected_skipped> skipped and <expected_errors> errors

    Examples: Valid Address Combinations (Should Migrate)
    | service_id | uid    | service_name                    | ods_code | public_name                     | postcode  | address                                | town        | expected_supported | expected_unsupported | expected_transformed | expected_migrated | expected_skipped | expected_invalid | expected_errors |
    | 600001     | 300001 | GP ValidFullAddress             | A12345   | Valid Full Address Surgery      | SO1 1AA   | 123 Main St$Building A$Hampshire       | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0                | 0               |
    | 600002     | 300002 | GP_ValidAddressNoTown           | B12345   | Valid Address No Town           | SO1 1AA   | 123 Main St$Hampshire                  |             | 1                  | 0                    | 1                    | 1                 | 0                | 0                | 0               |
    | 600003     | 300003 | GP_ValidAddressNoPostcode       | C12345   | Valid Address No Postcode       |           | 123 Main St$Hampshire                  | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0                | 0               |
    | 600004     | 300004 | GP_ValidAddressOnly             | D12345   | Valid Address Only              |           | 123 Main St$Hampshire                  |             | 1                  | 0                    | 1                    | 1                 | 0                | 0                | 0               |

    Examples: Invalid - All Fields Empty (Fatal Error)
    | service_id | uid    | service_name                    | ods_code | public_name                     | postcode  | address       | town          | expected_supported | expected_unsupported | expected_transformed | expected_migrated | expected_skipped | expected_invalid | expected_errors |
    | 600005     | 300005 | GP_AllFieldsEmpty               | E12345   | All Fields Empty                |           |               |               | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |

    Examples: Invalid - "Not Available" Address with No Town/Postcode (Fatal Error)
    | service_id | uid    | service_name                    | ods_code | public_name                     | postcode      | address       | town          | expected_supported | expected_unsupported | expected_transformed | expected_migrated | expected_skipped | expected_invalid | expected_errors |
    | 600006     | 300006 | GP_NotAvailableAll              | F12345   | Not Available All               | Not available | Not available | Not available | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |
    | 600007     | 300007 | GP_NotAvailableAddressOnly      | G12345   | Not Available Address Only      |               | Not available |               | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |

    Examples: Invalid - "Not Available" Address with Town Only (Fatal Error)
    | service_id | uid    | service_name                    | ods_code | public_name                     | postcode      | address       | town        | expected_supported | expected_unsupported | expected_transformed | expected_migrated | expected_skipped | expected_invalid | expected_errors |
    | 600008     | 300008 | GP_NotAvailableWithTown         | H12345   | Not Available With Town         |               | Not available | Southampton | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |
    | 600009     | 300009 | GP_NotAvailableAllTownValid     | J12345   | Not Available All Town Valid    | Not available | Not available | Southampton | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |

    Examples: Invalid - "Not Available" Address with Postcode Only (Fatal Error)
    | service_id | uid    | service_name                    | ods_code | public_name                     | postcode  | address       | town          | expected_supported | expected_unsupported | expected_transformed | expected_migrated | expected_skipped | expected_invalid | expected_errors |
    | 600010     | 300010 | GP_NotAvailableWithPostcode     | K12345   | Not Available With Postcode     | SO1 1AA   | Not available |               | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |
    | 600011     | 300011 | GP_NotAvailableAllPostcodeValid | L12345   | Not Available All Postcode      | SO1 1AA   | Not available | Not available | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |

    Examples: Invalid - "Not Available" Address with Town and Postcode (Fatal Error - Design Decision)
    | service_id | uid    | service_name                    | ods_code | public_name                     | postcode  | address       | town        | expected_supported | expected_unsupported | expected_transformed | expected_migrated | expected_skipped | expected_invalid | expected_errors |
    | 600012     | 300012 | GP_NotAvailableWithTownPostcode | M12345   | Not Available With Both         | SO1 1AA   | Not available | Southampton | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |

    Examples: Invalid - Empty Address with Town Only (Fatal Error - Address Field Required)
    | service_id | uid    | service_name                    | ods_code | public_name                     | postcode  | address | town        | expected_supported | expected_unsupported | expected_transformed | expected_migrated | expected_skipped | expected_invalid | expected_errors |
    | 600013     | 300013 | GP_EmptyAddressWithTown         | N12345   | Empty Address With Town         |           |         | Southampton | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |

    Examples: Invalid - Empty Address with Postcode Only (Fatal Error - Address Field Required)
    | service_id | uid    | service_name                    | ods_code | public_name                     | postcode  | address | town | expected_supported | expected_unsupported | expected_transformed | expected_migrated | expected_skipped | expected_invalid | expected_errors |
    | 600014     | 300014 | GP_EmptyAddressWithPostcode     | P12345   | Empty Address With Postcode     | SO1 1AA   |         |      | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |

    Examples: Invalid - Empty Address with Town and Postcode (Fatal Error - Address Field Required)
    | service_id | uid    | service_name                    | ods_code | public_name                     | postcode  | address | town        | expected_supported | expected_unsupported | expected_transformed | expected_migrated | expected_skipped | expected_invalid | expected_errors |
    | 600015     | 300015 | GP_EmptyAddressWithBoth         | V12345   | Empty Address With Both         | SO1 1AA   |         | Southampton | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |

    Examples: Invalid - Various "Not Available" Case Variations
    | service_id | uid    | service_name                    | ods_code | public_name                     | postcode      | address       | town          | expected_supported | expected_unsupported | expected_transformed | expected_migrated | expected_skipped | expected_invalid | expected_errors |
    | 600016     | 300016 | GP_NotAvailableLowercase        | W12345   | Not Available Lowercase         | not available | not available | not available | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |
    | 600017     | 300017 | GP_NotAvailableMixedCase        | Y12345   | Not Available Mixed Case        | Not Available | Not Available | Not Available | 1                  | 0                    | 0                    | 0                 | 0                | 1                | 0               |
