# FtRS Python Packages

This package includes all common Python packages used by the FtRS Directory of Services project.

## Current Packages

- `ftrs_data_layer` - responsible for direct database operations

## Installation

Poetry is used for dependency management and packaging. Ensure you have poetry installed, and then run `make install` to install packages.

> **Note:** Be sure to check that you are not currently in a virtual environment, and run `deactivate` to be sure to ensure dependencies in other projects are not polluted.

## Running Linting & Formatting

Linting and formatting are handled using Ruff. To run the linting in check mode, run `make lint`.

To run linting & formatting in fix mode, run:

```bash
poetry run ruff check --fix
poetry run ruff format
```

## Running Tests

Tests are run using Pytest. To run these tests, you can run:

```bash
make unit-test
### or
poetry run pytest
```

## Building the package

To build the project, run `make build`. This will store the output as wheel within `build/packages/python`.
