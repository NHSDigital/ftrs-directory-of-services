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
# take the latest dump from the bucket
aws s3 cp s3://ftrs-dos-dev-data-migration-pipeline-store/sanitised-clone/05-03-25/dos-pgdump.sql .tmp/dos-01-02-24.sql

# Load the dump into the local DB
# Ask team for values to substitute here
psql -d postgresql://<user>:<password>@<host>:<port>/postgres -f .tmp/dos-01-02-24.sql
```

This will create a new schema named 'pathwaysdos' containing the tables and data.

### Running the pipeline locally

The pipeline can be run locally using the `dos-etl` command. Ensure you are in the correct directory and have activated the Poetry environment.

```bash
# Activate Python virtual environment
eval $(poetry env activate)
```

The migration command accepts the following mandatory options:

- `--db-uri`: The URI of the source database. This should be in the format `postgresql://<user>:<password>@<host>:<port>/<database>`.
- `--env`: The environment to run the migration in. This should be either `local` or `dev`.

The following options are also available:

- `--workspace`: The workspace to run the migration in, for example `fdos-000`.
- `--ddb-endpoint-url`: The endpoint URL for the DynamoDB instance. This is required for local DynamoDB testing.
- `--service-id`: Only migrate data for a specific service ID. This is optional and can be used to limit the migration to a single service.
- `--output-dir`: Store output files in a specific directory. This skips loading into DynamoDB and is useful for debugging.

```bash
# Store output locally
dos-etl \
    --db-uri postgresql://<user>:<password>@<host>:<port>/<database> \
    --env local \
    --output-dir /tmp/out/extract.parquet

# Migrate all services directly into local DynamoDB
dos-etl \
    --db-uri postgresql://<user>:<password>@<host>:<port>/<database> \
    --env local \
    --ddb-endpoint-url http://localhost:8000


# Migrate a specific service directly into dev DynamoDB
dos-etl \
    --db-uri postgresql://<user>:<password>@<host>:<port>/<database> \
    --env dev \
    --service-id <service_id>

# Migrate all services directly into workspaced DynamoDB
dos-etl \
    --db-uri postgresql://<user>:<password>@<host>:<port>/<database> \
    --env local \
    --workspace fdos-000 \
    --ddb-endpoint-url http://localhost:8000
```
