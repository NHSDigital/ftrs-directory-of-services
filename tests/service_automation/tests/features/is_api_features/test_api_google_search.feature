@is-api @is-pipeline
Feature: API Search Playwright in Google

Scenario: API Search for Playwright in Google
  Given I make GET request to the Google search API
  When I receive the response
  Then I should see search results
