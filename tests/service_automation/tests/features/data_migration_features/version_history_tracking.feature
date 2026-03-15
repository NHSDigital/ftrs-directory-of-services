@data-migration @version-history
Feature: Version History Tracking

  Tests Lambda handler logic directly. Does NOT test DynamoDB Streams → Lambda integration.

  Background:
    Given the test environment is configured
    And DynamoDB tables are ready
    And the version history table exists

  Scenario: Organisation document update creates version history record
    Given an Organisation document exists in DynamoDB with
      | field       | value                                |
      | id          | aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa |
      | name        | Original Organisation Name           |
      | type        | user                                 |
    When the Organisation document is updated with changes
      | field       | value                                |
      | name        | Updated Organisation Name            |
    Then a version history record should exist with
      | attribute      | value                                                 |
      | entity_id      | organisation#aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa#document |
      | change_type    | UPDATE                                                |
    And the version history "changed_fields.document.values_changed.root['name'].new_value" should be "Updated Organisation Name"
    And the version history "changed_fields.document.values_changed.root['name'].old_value" should be "Original Organisation Name"
    And the version history "changed_by.type" should be "app"
    And the version history record should have a valid timestamp

  Scenario: No version history record for identical document values
    Given an Organisation document exists in DynamoDB with
      | field       | value                                |
      | id          | dddddddd-dddd-dddd-dddd-dddddddddddd |
      | status      | active                               |
      | type        | user                                 |
    When the Organisation document is updated with changes
      | field       | value                                |
      | status      | active                               |
    Then no version history record should be created for entity "organisation#dddddddd-dddd-dddd-dddd-dddddddddddd#document"

  Scenario: Organisation document creation creates version history record
    When a new Organisation document is created with
      | field       | value                                |
      | id          | bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb |
      | name        | New Organisation Name                |
      | type        | user                                 |
      | status      | active                               |
    Then a version history record should exist with
      | attribute      | value                                                 |
      | entity_id      | organisation#bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb#document |
      | change_type    | CREATE                                                |
    And the version history "changed_by.type" should be "app"
    And the version history record should have a valid timestamp

  Scenario: Organisation document deletion creates version history record
    Given an Organisation document exists in DynamoDB with
      | field       | value                                |
      | id          | cccccccc-cccc-cccc-cccc-cccccccccccc |
      | name        | Organisation To Delete               |
      | type        | user                                 |
      | status      | active                               |
    When the Organisation document is deleted
    Then a version history record should exist with
      | attribute      | value                                                 |
      | entity_id      | organisation#cccccccc-cccc-cccc-cccc-cccccccccccc#document |
      | change_type    | DELETE                                                |
    And the version history "changed_by.type" should be "app"
    And the version history record should have a valid timestamp
