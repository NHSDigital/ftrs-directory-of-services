@data-migration
Feature: Service Transformation with Address and County Variations

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario Outline: Migrate GP practice with various county positions in address
    Given a 'Service' exists called '<service_name>' in DoS with attributes:
      | key                 | value                     |
      | id                  | <service_id>              |
      | uid                 | <uid>                     |
      | name                | <service_name>            |
      | publicname          | <public_name>             |
      | typeid              | 100                       |
      | statusid            | 1                         |
      | odscode             | <ods_code>                |
      | createdtime         | 2024-01-01 10:00:00       |
      | modifiedtime        | 2024-01-01 10:00:00       |
      | openallhours        | false                     |
      | restricttoreferrals | false                     |
      | postcode            | <postcode>                |
      | address             | <address>                 |
      | town                | <town>                    |
      | web                 | https://www.nhs.uk/       |
      | email               | england.contactus@nhs.net |
      | publicphone         | 0300 311 22 33            |
    When a single service migration is run for ID '<service_id>'
    Then the metrics should be 1 total, <expected_supported> supported, <expected_unsupported> unsupported, <expected_transformed> transformed, <expected_inserted> inserted, 0 updated, <expected_skipped> skipped, 0 invalid and <expected_errors> errors
    And service ID '<service_id>' was transformed into 1 organisation, 1 location and 1 healthcare service
    And the service address for ID '<service_id>' should be:
      | key      | value             |
      | county   | <expected_county> |
      | line1    | <expected_line1>  |
      | line2    | <expected_line2>  |
      | postcode | <postcode>        |
      | town     | <town>            |

    Examples: County in Last Segment (Standard Format)
      | service_id | uid    | service_name               | ods_code | public_name                | postcode | address                                    | town         | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1          | expected_line2 |
      | 700001     | 400001 | GP_CountyLastStandard      | A11111   | County Last Standard       | HA8 0AD  | Cleator Moor Health Ctr$Birks Road$Cumbria | Cleator Moor | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Cumbria         | Cleator Moor Health Ctr | Birks Road     |
      | 700002     | 400002 | GP_CountyLastHampshire     | B11111   | County Last Hampshire      | SO1 1AA  | 123 Main St$Building A$Hampshire           | Southampton  | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St             | Building A     |
      | 700003     | 400003 | GP_CountyLastGreaterLondon | C11111   | County Last Greater London | SW1A 1AA | Parliament St$Westminster$Greater London   | London       | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Greater London  | Parliament St           | Westminster    |
      | 700004     | 400004 | GP_CountyLastWestYorkshire | D11111   | County Last West Yorkshire | LS1 1AB  | City Square$Leeds Centre$West Yorkshire    | Leeds        | 1                  | 0                    | 1                    | 1                 | 0                | 0               | West Yorkshire  | City Square             | Leeds Centre   |

    Examples: County in First Segment
      | service_id | uid    | service_name            | ods_code | public_name            | postcode | address                                    | town         | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1          | expected_line2 |
      | 700005     | 400005 | GP_CountyFirstCumbria   | E11111   | County First Cumbria   | HA8 0AD  | Cumbria$Cleator Moor Health Ctr$Birks Road | Cleator Moor | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Cumbria         | Cleator Moor Health Ctr | Birks Road     |
      | 700006     | 400006 | GP_CountyFirstHampshire | F11111   | County First Hampshire | SO1 1AA  | Hampshire$123 Main St$Building A           | Southampton  | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St             | Building A     |

    Examples: County in Middle Segment
      | service_id | uid    | service_name                | ods_code | public_name                 | postcode | address                                     | town         | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1          | expected_line2 |
      | 700007     | 400007 | GP_CountyMiddleCumbria      | H11111   | County Middle Cumbria       | HA8 0AD  | Cleator Moor Health Ctr$Cumbria$Birks Road  | Cleator Moor | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Cumbria         | Cleator Moor Health Ctr | Birks Road     |
      | 700008     | 400008 | GP_CountyMiddleHampshire    | J11111   | County Middle Hampshire     | SO1 1AA  | 123 Main St$Hampshire$Building A            | Southampton  | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St             | Building A     |
      | 700009     | 400009 | GP_CountyMiddleMultiSegment | K11111   | County Middle Multi Segment | SW1A 1AA | First Line$Greater London$Second Line$Third | London       | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Greater London  | First Line              | Second Line    |

    Examples: County Only (Single Segment)
      | service_id | uid    | service_name           | ods_code | public_name           | postcode | address   | town        | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1 | expected_line2 |
      | 700010     | 400010 | GP_CountyOnlyHampshire | M11111   | County Only Hampshire | SO1 1AA  | Hampshire | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       |                |                |

    Examples: No County Present
      | service_id | uid    | service_name            | ods_code | public_name             | postcode | address                     | town        | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1 | expected_line2 |
      | 700011     | 400011 | GP_NoCountyTwoSegments  | P11111   | No County Two Segments  | SO1 1AA  | 123 Main St$Building A      | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               |                 | 123 Main St    | Building A     |
      | 700012     | 400012 | GP_NoCountyOneSegment   | V11111   | No County One Segment   | SO1 1AA  | 123 Main St                 | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               |                 | 123 Main St    |                |
      | 700013     | 400013 | GP_NoCountyManySegments | W11111   | No County Many Segments | HA8 0AD  | Line 1$Line 2$Line 3$Line 4 | Edgware     | 1                  | 0                    | 1                    | 1                 | 0                | 0               |                 | Line 1         | Line 2         |

    Examples: Multiple Counties (Last to First Priority)
      | service_id | uid    | service_name                | ods_code | public_name                 | postcode | address                              | town   | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1 | expected_line2 |
      | 700014     | 400014 | GP_MultiCountyLastWins      | Y11111   | Multi County Last Wins      | SW1A 1AA | Hampshire$123 Main St$Greater London | London | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Greater London  | Hampshire      | 123 Main St    |
      | 700015     | 400015 | GP_MultiCountyThreeCounties | A11111   | Multi County Three Counties | LS1 1AB  | Hampshire$Cumbria$West Yorkshire     | Leeds  | 1                  | 0                    | 1                    | 1                 | 0                | 0               | West Yorkshire  | Hampshire      | Cumbria        |

    Examples: County with Whitespace Variations
      | service_id | uid    | service_name                | ods_code | public_name                | postcode | address                              | town        | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1 | expected_line2 |
      | 700016     | 400016 | GP_CountyLeadingWhitespace  | A22222   | County Leading Whitespace  | SO1 1AA  | 123 Main St$  Hampshire              | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    |                |
      | 700017     | 400017 | GP_CountyTrailingWhitespace | B22222   | County Trailing Whitespace | SO1 1AA  | 123 Main St$Hampshire  $Building A   | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    | Building A     |
      | 700018     | 400018 | GP_CountyBothWhitespace     | C22222   | County Both Whitespace     | SO1 1AA  | 123 Main St$  Hampshire  $Building A | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    | Building A     |

    Examples: County Case Variations
      | service_id | uid    | service_name       | ods_code | public_name       | postcode | address                          | town        | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1 | expected_line2 |
      | 700019     | 400019 | GP_CountyLowercase | D22222   | County Lowercase  | SO1 1AA  | 123 Main St$hampshire$Building A | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    | Building A     |
      | 700020     | 400020 | GP_CountyUppercase | E22222   | County Uppercase  | SO1 1AA  | 123 Main St$HAMPSHIRE$Building A | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    | Building A     |
      | 700021     | 400021 | GP_CountyMixedCase | F22222   | County Mixed Case | SO1 1AA  | 123 Main St$HaMpShIrE$Building A | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    | Building A     |

    Examples: County with Town Matching in Address
      | service_id | uid    | service_name              | ods_code | public_name               | postcode | address                             | town        | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1 | expected_line2 |
      | 700022     | 400022 | GP_CountyTownInAddress    | G22222   | County Town In Address    | SO1 1AA  | 123 Main St$Southampton$Hampshire   | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    |                |
      | 700023     | 400023 | GP_CountyTownBeforeCounty | H22222   | County Town Before County | LS1 1AB  | Leeds$City Centre$West Yorkshire    | Leeds       | 1                  | 0                    | 1                    | 1                 | 0                | 0               | West Yorkshire  | City Centre    |                |
      | 700024     | 400024 | GP_CountyTownAfterCounty  | J22222   | County Town After County  | SW1A 1AA | Greater London$London$Parliament St | London      | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Greater London  | Parliament St  |                |

    Examples: County with Duplicate Segments
      | service_id | uid    | service_name               | ods_code | public_name               | postcode | address                                     | town        | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1 | expected_line2 |
      | 700025     | 400025 | GP_CountyDuplicateSegments | K22222   | County Duplicate Segments | SO1 1AA  | 123 Main St$123 main st$Hampshire           | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    |                |
      | 700026     | 400026 | GP_CountyDuplicateAfter    | L22222   | County Duplicate After    | SO1 1AA  | 123 Main St$Hampshire$Building A$building a | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    | Building A     |

    Examples: Edge Cases - Empty and Separator Handling
      | service_id | uid    | service_name                | ods_code | public_name                | postcode | address                          | town        | expected_supported | expected_unsupported | expected_transformed | expected_inserted | expected_skipped | expected_errors | expected_county | expected_line1 | expected_line2 |
      | 700027     | 400027 | GP_CountyLeadingSeparators  | Y22222   | County Leading Separators  | SO1 1AA  | $123 Main St$Hampshire           | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    |                |
      | 700028     | 400028 | GP_CountyTrailingSeparators | A22222   | County Trailing Separators | SO1 1AA  | 123 Main St$Hampshire$           | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    |                |
      | 700029     | 400029 | GP_CountyMiddleSeparators   | B33333   | County Middle Separators   | SO1 1AA  | 123 Main St$Hampshire$Building A | Southampton | 1                  | 0                    | 1                    | 1                 | 0                | 0               | Hampshire       | 123 Main St    | Building A     |
