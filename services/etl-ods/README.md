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

Runs ruff check and ruff format

```bash
make lint
```

To automatically format Python code and fix some linting issues, you can use:

```bash
eval $(poetry env activate)

poetry run ruff check --fix
poetry run ruff format
```

### Building the Lambda Package and Dependency Layers

Set the environment variables

```bash
export LOCAL_CRUD_API_URL=http://localhost:8001
export LOCAL_API_KEY= #api key from dev portal
export LOCAL_PRIVATE_KEY= #key filepath
export LOCAL_KID= #kid from dev portal
export LOCAL_TOKEN_URL=https://internal-dev.api.service.nhs.uk/oauth2/token
```

To package the Lambda function package and create the dependency layers, run:

```bash
make build
```
