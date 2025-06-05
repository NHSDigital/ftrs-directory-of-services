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

Once the dynamo-db instance is running and tables created run

## To start the API locally, run the following command from the crud-apis/ directory

```bash
make start-organisations-api
```

The API will now be running on [http://localhost:8001]

## API Endpoints

### Read Organisation

**Endpoint**: `GET /{organisation_id}`

**Description**: Reads an organisation with the given ID.

**Path Parameters**:

- `organisation_id` (UUID): The internal ID of the organisation.

### Read Many Organisation

**Endpoint**: `GET /`

**Description**: Reads many organisations with a given limit.

**Path Parameters**:

- `limit` (int): The number of records to be read.

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

### Get Organisation by ODS Code

**Endpoint**: `GET /ods/{ods_code}`

**Description**: Retrieves an organisation by its ODS code.

**Path Parameters**:

- `ods_code` (string): The ODS code of the organisation.
