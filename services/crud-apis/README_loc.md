# FtRS Location API

## Overview

The Location API provides endpoints to manage locations. It is built using FastAPI and is designed to be deployed as a Lambda function or run locally for development and testing.

## Installation

### Prerequisites

This project requires Python and Poetry as core dependencies.
The current versions of these can be found in the `.tool-versions` file, and can be installed using asdf.

### Install Dependencies

Navigate to the `location` directory and install the dependencies using Poetry:

```bash
cd services/crud-apis/location
poetry install
```

### Environment Variables

The following environment variables are required for the application to run:

- `ENVIRONMENT`: The environment in which the application is running (e.g., `local`, `dev`, `prod`).
- `WORKSPACE`: The workspace name for the application.
- `ENDPOINT_URL`: The URL of the DynamoDB endpoint (e.g., `http://localhost:8000` for local development).

Set these variables in a local `.env` file or export them in your terminal session.See the `default.env` file for a template.

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

Unit tests are run using Pytest. You can use the make target to conveniently run these tests or run them directly using pytest.

```bash
make unit-test
# or
eval $(poetry env activate)
pytest tests
```

### Running Lambda Steps Locally

1. Add environment variables see the `default.env` file for a template.
2.Follow the guidance in services/data-migration/README.md to initialise the dynamo-db table
  Once the dynamo-db instance is running and tables are created
2. Run the following command to start the API locally in the **location** directory:

from the crud-apis directory run:

```bash
poetry run poe start-location-api
```

The API will be available at [http://localhost:6000].

## API Endpoints

The API routing happens at the API gateway level, routing will happen for the /location path.

### Get Location by ID

**Endpoint**: GET /{location_id}

**Description**: Retrieves a location by its UUID.

**Path Parameters**: location_id (UUID): The ID of the location.

**Responses**:
 200 OK: Returns the location details.
 400 Bad Request: Invalid UUID format.
 404 Not Found: Location not found.

### Get All locations (Current page limit is set to 10)

**Endpoint**: GET /

**Description**: Retrieves all locations.

**Responses**: 200 OK: Returns a list of locations.

### Create Location

**Endpoint**: POST /

**Description**: Creates a new location.

**Request Body**: JSON object containing the location details.

**Responses**:
 201 Created: Returns the created location.
 422 Unprocessable entities: Invalid request body.

### Delete Location

**Endpoint**: DELETE /{location_id}

**Description**: Deletes a location with given ID.

**Path Parameters**: location_id (UUID): The ID of the location.

**Responses**:
 204 No Content: Request fulfilled, nothing follows.
 404 Not Found: Location not found.

### Update Location

**Endpoint**: PUT /{location_id}

**Description**: Updates a location with the given ID.

**Path Parameters**:

- `location_id` (UUID): The internal ID of the location.

**Request Body**:

- A JSON object containing the fields to update. Example:

  ```json
  {
    "name": "New Location Name"
  }
  ```

**Responses**:

 200 OK: Returns the updated location.
 404 Not Found: Service to be updated not found.
 422 Unprocessable Entity: Invalid request body.
