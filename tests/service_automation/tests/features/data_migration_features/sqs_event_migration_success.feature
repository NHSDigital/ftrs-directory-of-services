@data-migration @ftrs-pipeline
Feature: Run Single Service Migration
  As a test author
  I want to execute a data migration triggered by an SQS event
  So that I can verify the migration process correctly handles service insert events and updates the target system without errors

  Background:
    Given the test environment is configured
    And the DoS database has test data
    And DynamoDB tables are ready

  Scenario: Process SQS event for service INSERT
    Given a 'Service' exists called 'SQSTestService' in DoS with attributes:
      | key                 | value                                      |
      | id                  | 300010                                     |
      | uid                 | 200010                                     |
      | name                | SQSTestGPPractice                          |
      | publicname          | SQS Test GP Practice                       |
      | typeid              | 100                                        |
      | statusid            | 1                                          |
      | odscode             | B12345                                     |
      | createdtime         | 2024-01-01 10:00:00                        |
      | modifiedtime        | 2024-01-01 10:00:00                        |
      | openallhours        | false                                      |
      | restricttoreferrals | false                                      |
      | postcode            | SW1A 1AA                                   |
      | address             | Westminster                                |
      | town                | London                                     |
      | web                 | https://www.nhs.uk/                        |
      | email               | test@nhs.net                               |
      | publicphone         | 0300 311 22 33                             |
    When the data migration process is run with the event:
      """
      {
        "Records": [
          {
            "messageId": "test-message-1",
            "receiptHandle": "test-receipt-handle",
            "body": "{\"type\": \"dms_event\", \"record_id\": 300010, \"table_name\": \"services\", \"method\": \"insert\"}",
            "attributes": {
              "ApproximateReceiveCount": "1",
              "SentTimestamp": "1704106800000",
              "SenderId": "EXAMPLE123456789012",
              "ApproximateFirstReceiveTimestamp": "1704106800000"
            },
            "messageAttributes": {},
            "md5OfBody": "test-md5",
            "eventSource": "aws:sqs",
            "awsRegion": "eu-west-2"
          }
        ]
      }
      """
    Then the SQS event metrics should be 1 total, 1 supported, 0 unsupported, 1 transformed, 1 migrated, 0 skipped and 0 errors
