@data-migration
Feature: Data Migration

  Scenario: Smoke test for GP practice migration
    Given clear out service by id
    Given service is created
    Then dynamo update happens
