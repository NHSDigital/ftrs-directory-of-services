# FtRS Organisation API

## Overview

The Healthcare Service API provides endpoints to manage healthcare services. It is built using FastAPI and is designed to be deployed as a Lambda function or run locally for development and testing.

## Installation

### Prerequisites

This project requires Python and Poetry as core dependencies.
The current versions of these can be found in the `.tool-versions` file, and can be installed using asdf.

### Install Dependencies

Navigate to the `healthcare_service` directory and install the dependencies using Poetry:

```bash
cd services/crud-apis/healthcare_service
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
2. Run the following command to start the API locally in the **healthcare_service** directory:

```bash
poetry run start-healthcare-api
```

The API will be available at [http://localhost:7000].

## API Endpoints

The API routing happens at the API gateway level, routing will happen for the /healthcareservice path.

### Get Healthcare Service by ID

**Endpoint**: GET /{service_id}

**Description**: Retrieves a healthcare service by its UUID.

**Path Parameters**: service_id (UUID): The ID of the healthcare service.

**Responses**:
 200 OK: Returns the healthcare service details.
 400 Bad Request: Invalid UUID format.
 404 Not Found: Service not found.

### Get All Healthcare Services (Current page limit is set to 10)

**Endpoint**: GET /

**Description**: Retrieves all healthcare services.

**Responses**: 200 OK: Returns a list of healthcare services.
