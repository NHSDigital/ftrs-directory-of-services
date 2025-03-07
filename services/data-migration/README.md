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
# Activate Python virtual environment
eval $(poetry env activate)

# Run the linter
ruff check

# Run the formatter
ruff format

# Run the formatter in check mode
ruff format --check
```

### Start Database Container

For local development, this project relies on a local Postgres instance running in a docker container.
This container will persist data at `./.tmp/pg_data/`.

```bash
mkdir -p ./.tmp/pg_data
podman compose up -d
```

### Setting Database Schema

To set the target database schema manually, run the following script to load the schema.

```bash
# Activate Python virtual environment
eval $(poetry env activate)

# Run Schema Load Script
python -m pipeline.schema \
    --db-uri {target_database} \
    --schema-path schema/target-state.sql
```

The script will run a full refresh of the schemas, you will need to refresh your schema list on tools like pgAdmin.

All options can be found by running `python -m pipeline.schema --help`.

### Loading the local data clone

A sanitised clone of the source DoS data is available in S3.
This can be loaded into your local instance of Postgres to enable easier development.

```bash
# Assume role within UEC DOS DEV AWS account
# Copy source postgres dump
aws s3 cp s3://ftrs-dos-data-migration/sanitised-clone/pathwaysdos-pgdump.sql .tmp/pathwaysdos-01-02-24.sql

# Load the dump into the local DB
psql -d postgres://<user>:<password>@<host>:<port>/postgres -f .tmp/pathwaysdos-01-02-24.sql
```

This will create a new schema named 'pathwaysdos' containing the tables and data.

### Running Pipeline Steps Locally

```bash
# Activate Python virtual environment
eval $(poetry env activate)

# Run extraction step
python -m pipeline.extract \
    --db-uri {source_database} \
    --output-path /tmp/out/extract/

# Run transformation step
python -m pipeline.transform \
    --input-path /tmp/out/extract/ \
    --output-path /tmp/out/transform/

# Run load step
python -m pipeline.load \
    --db-uri {target_database} \
    --input-path /tmp/out/transform/
```
