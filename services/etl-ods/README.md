# ETL ODS Pipeline

## Installation

This project requires Python and Poetry as core dependencies. test.
The current versions of these can be found in the `.tool-versions` file, and can be installed using asdf.

### Install Python Dependencies

```bash
cd services/etl-ods
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

# Run extraction

python cli.py 2025-05-01

```
The date here being what day you want to start extracting data from.
