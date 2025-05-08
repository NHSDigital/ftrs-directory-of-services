# FtRS Organisation API

## Installation

This project requires Python and Poetry as core dependencies.
The current versions of these can be found in the `.tool-versions` file, and can be installed using asdf.

### Install Python Dependencies

```bash
cd services/crud-apis/organisations
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

### Running Lambda Steps Locally

Add environment variables but running

```bash
export ENVIRONMENT=local
export WORKSPACE=local_workspace
export ENDPOINT_URL=http://localhost:8000
```

Follow the guidance in services/data-migration/README.md to initiliase the dynamo-db table

Once the dynamo-db instance running and tables created run

```bash
make start-api
```

The API will now be running on [http://localhost:8001]

## API Endpoints

### Update Organisation

**Endpoint**: `PUT /{organisation_id}`

**Description**: Updates an organisation with the given ID.

**Path Parameters**:

- `organisation_id` (UUID): The internal ID of the organisation.

**Request Body**:

- A JSON object containing the fields to update. Example:

  ```json
  {
    "name": "New Organisation Name",
  }
  ```
