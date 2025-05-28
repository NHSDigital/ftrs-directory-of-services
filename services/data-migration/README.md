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


### Running Pipeline Steps Locally

The pipeline can be run locally using the `dos-etl` command. Ensure you are in the correct directory and have activated the Poetry environment.

```bash
# Activate Python virtual environment
eval $(poetry env activate)
```

#### Extract

The extract step accepts the following options:

- `--db-uri`: The URI of the source database. This should be in the format `postgresql://<user>:<password>@<host>:<port>/<database>`.
- `--output`: The output path for the extracted data. This can be a local path or an S3 URI.

```bash
# Store output locally
dos-etl extract \
    --db-uri postgresql://<user>:<password>@<host>:<port>/<database> \
    --output /tmp/out/extract.parquet

# Store output in S3
dos-etl extract \
    --db-uri postgresql://<user>:<password>@<host>:<port>/<database> \
    --output s3://<s3_bucket_name>/<s3_bucket_path>/extract.parquet
```

#### Transform

The transform step accepts the following options:

- `--input`: The input path for the extracted data. This can be a local file path or an S3 URI.
- `--output`: The output path for the transformed data. This can be a local file path or an S3 URI.

```bash
# Store output locally
dos-etl transform \
    --input /tmp/out/extract.parquet \
    --output /tmp/out/transform.parquet

# Store output in S3
dos-etl transform \
    --input s3://<s3_bucket_name>/<s3_bucket_path>/extract.parquet \
    --output s3://<s3_bucket_name>/<s3_bucket_path>/transform.parquet
```

#### Load

The load step accepts the following options:

- `--env`: The environment to load the data into. This can currently only be `local` or `dev`.
- `--workspace`: The workspace to load the data into. This is optional.
- `--endpoint-uri`: The endpoint URI for the DynamoDB instance. This is required for local testing.
- `--input`: The input path for the transformed data. This can be a local file path or an S3 URI.

```bash
# Load data from local directory into local DynamoDB
dos-etl load \
    --env local \
    --endpoint-uri http://localhost:8000 \
    --input /tmp/out/transform.parquet

# Load data from S3 into dev DynamoDB
dos-etl load \
    --env dev \
    --input s3://<s3_bucket_name>/<s3_bucket_path>/transform.parquet
```
