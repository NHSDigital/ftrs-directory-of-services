@data-migration
Feature: Data Migration Hello World

  Scenario: Hello world scenario for data migration
    Given the data migration system is ready
    When I run the hello world data migration test
    Then I see a hello world result

    And the 'organisation' for service ID '12345' has content:
      """
      {
        "id": "4613555d-a4c0-4353-88bd-611431bf25b0",
        "name": "Some Place, Some Town"
        
      }
      """