# Running OpenSearch Locally with Docker Compose

This document explains how to set up and run OpenSearch locally using Docker Compose, including the necessary configuration for Data Prepper to sync data from DynamoDB.

## Prerequisites

- Docker and Docker Compose installed
- AWS CLI (for DynamoDB interactions)

## Setup and Configuration

### 1. Required Configuration Files

#### a. `pipelines.yaml` provided in the local-opensearch-config directory

Make sure to give ARN of the local table in the `pipelines.yaml` file under the `dynamodb` section.

#### b. `data-prepper-config.yaml` provided in the local-opensearch-config directory

#### c. `index-template.json` for OpenSearch Index Template provided in the local-opensearch-config directory

This file defines the index template for OpenSearch to handle DynamoDB data.
this can be included in the pipelines.yaml under the `index_template` section.

### 3. Initialize DynamoDB Table

Create the required stream for the dynamoDB table by running the following command:(replace `<your-table-name>` with your actual table name)

```bash

aws dynamodb update-table \
  --table-name <your-table-name> \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
  --endpoint-url http://localhost:8000

```

Start postion are pointed to the latest stream record so that only new records are processed into the shards of the Data Prepper pipeline.
To test the opensearch successfully, you can add some test data to the DynamoDB table.

### 3. Start the Environment

Go to the data-migration and run the following command to start the services:

```bash

export ENABLE_OPENSEARCH=enabled
# Enable OpenSearch when starting the services
docker compose --profile enabled up

```

This will start:

- DynamoDB Local (port 8000)
- OpenSearch (port 9200)
- Data Prepper
- PostgreSQL (port 5432)

### 4. Add Test Data

1. Add some test data by running a POST request from the crud-apis service

2. Alternatively, you can use the AWS CLI to add test data:

```bash

aws dynamodb put-item \
    --table-name <your-table-name> \
    --item '{"id": {"S": "1"}, "name": {"S": "Test Item"}, "value": {"N": "100"}}' \
    --endpoint-url http://localhost:8000

```

### 5. Configure Data Prepper

Ensure that the `pipelines.yaml` and `data-prepper-config.yaml` files are correctly set up to connect to your DynamoDB table and OpenSearch instance.
The `pipelines.yaml` should include the necessary pipeline configurations for reading from DynamoDB and writing to OpenSearch.

## Verification

### Verify OpenSearch is Running

```bash
curl http://localhost:9200
```

### Verify Data Synchronization

Check if data has been indexed in OpenSearch:
Note that the index name in the `pipelines.yaml` should match the one you are querying.(e.g., `ftrs-organisation`)

```bash
curl http://localhost:9200/ftrs-organisation/_search

```

### Search for Specific Data

To verify that specific data has been indexed, you can run a search query. For example, to search for an organisation with ODS Code `O896547`:

```bash
curl -X GET "http://localhost:9200/ftrs-organisation/_search?q=O896547&pretty"

```

### Monitor Data Prepper Logs

```bash
docker-compose logs -f data-prepper

```

### Monitor OpenSearch Logs

```bash
docker-compose logs -f opensearch

```

## Troubleshooting

1. **Data Prepper connection issues**: Ensure ARNs in `pipelines.yaml` match your actual table ARN.

2. **Stream consumption errors**: Check that DynamoDB streams are enabled on your table.

3. **Coordination errors**: Verify that the Data Prepper coordination table is created correctly.

4. **OpenSearch connection issues**: Ensure that the OpenSearch service is running and accessible at `http://localhost:9200`.

5. **AWS CLI configuration**: Ensure your AWS CLI is configured correctly with valid credentials. You can run `aws configure` to set up your credentials.
Add local profile into `~/.aws/credentials` file to avoid any issues with AWS CLI commands

``` ini

[default]
[local]
aws_access_key_id=dummy
aws_secret_access_key=dummy
aws_session_token=dummy
aws_region=eu-west-1

```

The above credentials are required because the Data Prepper pipeline uses AWS SDK to connect to DynamoDB and OpenSearch, and it requires valid credentials to authenticate even for local development.

## Cleanup

```bash
docker-compose down -v

```

## Note

The docker compose downloads the latest version of OpenSearch and Data Prepper images.so we don't need to build the images manually or locally.
