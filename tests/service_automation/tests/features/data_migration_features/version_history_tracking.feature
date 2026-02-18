@data-migration @version-history
Feature: Version History Tracking
  Track changes to Organisation, Location, and HealthcareService records via DynamoDB streams

  Background:
    Given the test environment is configured
    And DynamoDB tables are ready
    And the version history table exists

  Scenario: Organisation field update creates version history record
    Given an Organisation record exists in DynamoDB with
      | field       | value                                |
      | id          | aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa |
      | field       | name                                 |
      | value       | Original Organisation Name           |
    When the Organisation field "name" is updated to "Updated Organisation Name"
    Then a version history record should exist with
      | attribute      | value                                            |
      | entity_id      | organisation\|aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa\|name |
      | change_type    | UPDATE                                           |
    And the version history "changed_fields.name.old" should be "Original Organisation Name"
    And the version history "changed_fields.name.new" should be "Updated Organisation Name"
    And the version history "changed_by.type" should be "app"
    And the version history record should have a valid timestamp

  Scenario: Location field update creates version history record
    Given a Location record exists in DynamoDB with
      | field       | value                                |
      | id          | bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb |
      | field       | status                               |
      | value       | pending                              |
    When the Location field "status" is updated to "active"
    Then a version history record should exist with
      | attribute      | value                                            |
      | entity_id      | location\|bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb\|status |
      | change_type    | UPDATE                                           |
    And the version history "changed_fields.status.old" should be "pending"
    And the version history "changed_fields.status.new" should be "active"
    And the version history record should have a valid timestamp

  Scenario: HealthcareService field update creates version history record
    Given a HealthcareService record exists in DynamoDB with
      | field       | value                                |
      | id          | cccccccc-cccc-cccc-cccc-cccccccccccc |
      | field       | active                               |
      | value       | false                                |
    When the HealthcareService field "active" is updated to "true"
    Then a version history record should exist with
      | attribute      | value                                                  |
      | entity_id      | healthcare-service\|cccccccc-cccc-cccc-cccc-cccccccccccc\|active |
      | change_type    | UPDATE                                                 |
    And the version history "changed_fields.active.old" should be "false"
    And the version history "changed_fields.active.new" should be "true"
    And the version history record should have a valid timestamp

  Scenario: No version history record for identical values
    Given an Organisation record exists in DynamoDB with
      | field       | value                                |
      | id          | dddddddd-dddd-dddd-dddd-dddddddddddd |
      | field       | status                               |
      | value       | active                               |
    When the Organisation field "status" is updated to "active"
    Then no version history record should be created for entity "organisation|dddddddd-dddd-dddd-dddd-dddddddddddd|status"
