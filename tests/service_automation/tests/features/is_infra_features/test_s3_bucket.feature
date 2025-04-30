@is-infra
Feature: S3 Bucket Name Validation

Background: Check bucket exists
  Given I can see the S3 bucket "gp-search-s3" for stack "gp-search"

  Scenario: get a s3 bucket
    Given I upload the file "s3_data" to the s3 bucket
    Then I can download the file "s3_data" from the s3 bucket
    And the file contains 4 rows
    And I can delete the file "s3_data" from the s3 bucket

  Scenario: Validate AWS S3 bucket names
    Given I am authenticated with AWS CLI
    When I fetch the list of S3 buckets
    Then the bucket names should be valid
