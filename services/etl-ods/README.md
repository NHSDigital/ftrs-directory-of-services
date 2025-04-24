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

dos-etl extract \
    --ods-uri "https://digital.nhs.uk/services/organisation-data-service/organisation-data-service-apis/technical-guidance-ord/sync-endpoint"

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
