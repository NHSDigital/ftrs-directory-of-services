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
poetry env activate

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
podman compose up -d
```

### Setting Database Schema

To set the target database schema manually, run the following script to load the schema.

```bash
# Activate Python virtual environment
poetry env activate

# Run Schema Load Script
python -m pipeline.schema \
    --db-uri {target_database} \
    --schema-path schema/target-state.sql
```

If you are making changes to this database schema during development, you can provide the `--drop` flag to drop the existing schema before loading the provided schema.

If you are working with a schema with a different name, you can specify the `--drop-schema-name <name>` option to manually specify the schema to be dropped. This will default to `"Core"`.

All options can be found by running `python -m pipeline.schema --help`.

### Running Pipeline Steps Locally

```bash
# Activate Python virtual environment
poetry env activate

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
