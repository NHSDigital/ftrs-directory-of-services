# Data Migration Pipeline

## Installation

This project requires Python and Poetry as core dependencies.
The current versions of these can be found in the `.tool-versions` file, and can be installed using asdf.

### Install Python Dependencies

```bash
cd services/data-migration
poetry install
```

### Running Linting

Python code is linted and formatted using Ruff. The rules and arguments enabled can be found in the `pyproject.toml` file.

```bash
make lint # Runs ruff check and ruff format
```

To automatically format Python code and fix some linting issues, you can use:

```bash
eval $(poetry env activate)

ruff check --fix  # Runs linting with fix mode enabled
ruff format       # Runs the python code formatter
```

### Building the Lambda Package and Dependency Layers

To package the Lambda function package and create the dependency layers, run:

```bash
make build
```

### Running Tests

Unit tests are run using Pytest. You can use the make target to conveniently run these tests, or run them directly using pytest.

```bash
make unit-test
# or
eval $(poetry env activate)
pytest tests/unit
```

### Start Database Container

For local development, this project relies on a local Postgres instance running in a docker container.
This container will persist data at `./.tmp/pg_data/`.

```bash
cd services/data-migration
mkdir -p ./.tmp/pg_data
podman compose up -d
```

Note it may be necessary on first run to edit the context defined in docker-compose.yml

```context: ../../infrastructure/images/postgres```

### Loading the local data clone

A sanitised clone of the source DoS data is available in S3.
This can be loaded into your local instance of Postgres to enable easier development.

```bash
# install psql
brew install libpq
brew link --force libpq
```

```bash
# Assume role within UEC DOS DEV AWS account
# Copy source postgres dump
aws s3 cp s3://ftrs-dos-data-migration-pipeline-store-dev/sanitised-clone/01-02-24/dos-pgdump.sql .tmp/dos-01-02-24.sql

# Load the dump into the local DB
# Ask team for values to substitute here
psql -d postgresql://<user>:<password>@<host>:<port>/postgres -f .tmp/dos-01-02-24.sql
```

This will create a new schema named 'pathwaysdos' containing the tables and data.

### Setting up the local DynamoDB tables

Before running the load steps of the pipeline locally, you will need to create the DynamoDB tables locally.
This can be done using the `dos-etl reset` command.

```bash
# Create the local DynamoDB tables
dos-etl reset \
    --init \
    --env local \
    --endpoint-uri http://localhost:8000 \
```

The script can be aborted at the first prompt.

### Clearing Down DynamoDB Tables

To clear down the DynamoDB tables locally, you can delete them using NoSQL Workbench or the AWS CLI.

For deployed environments, you can use the `dos-etl reset` command to delete data within the existing tables.

```bash
# Delete the local DynamoDB data
dos-etl reset \
    --env local \
    --endpoint-uri http://localhost:8000

# Delete the dev DynamoDB data
dos-etl reset --env dev

# Delete a workspaced dev DynamoDB table
dos-etl reset --env dev --workspace my-workspace
```

### Running Pipeline Steps Locally

```bash
# Activate Python virtual environment
eval $(poetry env activate)

# Run extraction step - store output locally
dos-etl extract \
    --db-uri {source_database} \
    --output-path /tmp/out/extract/

# Run extraction step - store output in s3
dos-etl extract \
    --db-uri {source_database} \
    --s3-output-uri s3://<s3_bucket_name>/<s3_bucket_path>

# Run transformation step
dos-etl transform \
    --input-path /tmp/out/extract/ \
    --output-path /tmp/out/transform/

# Run load step
dos-etl load \
    --env {env} \ # use 'local' for local testing
    --endpoint-uri {ddb_endpoint} \
    --input-path /tmp/out/transform/
```
