@is-infra @is-pipeline @data-repo
Feature: Data Repository

  Scenario: Retrieve organisation model from seeded repository
    Given I have a organisation repo that is seeded
    When I get a model with id "dbb206d6-6cf7-43a4-b910-10fdc14a3cb6" from the repo
    Then a model of type Organisation is returned
    And the model has an id of "dbb206d6-6cf7-43a4-b910-10fdc14a3cb6"

  Scenario: Retrieve created model from repository
    Given I have a organisation repo
    And I create a model in the repo from json file "Organisation/organisation-with-4-endpoints.json"
    When I get a model with id "36fce427-0f31-4a4e-903f-74dcf9e63cfd" from the repo
    Then a model of type Organisation is returned
    And the model has an id of "36fce427-0f31-4a4e-903f-74dcf9e63cfd"

  Scenario: Retrieve non-existent model from repository
    Given I have a organisation repo
    When I get a model with id "INVALID" from the repo
    Then the model is not returned
