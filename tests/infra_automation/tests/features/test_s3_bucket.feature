Feature: S3 Bucket Name Validation

  Scenario: Validate AWS S3 bucket names
    Given I am authenticated with AWS CLI
    When I fetch the list of S3 buckets
    Then the bucket names should be valid


  Scenario: Check that specific bucket exists
    Given the S3 bucket exists
