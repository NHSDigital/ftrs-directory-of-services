# FTRS AWS Local

This package provides a set of tools to manage local AWS resources for the FTRS project, including DynamoDB and
Postgres.

## Current Packages

- `ftrs_aws_local` - responsible for managing local AWS resources such as DynamoDB etc

## Installation

Poetry is used for dependency management and packaging. Ensure you have poetry installed,
 and then run `poetry install` to install packages from the **ftrs_aws_local** package.

## Start Database Container

For local development, this project relies on a local Postgres and local DynamoDB instance running in a docker
container.
This container will persist data at `./.tmp/pg_data/`.

```bash
cd services/data-migration
mkdir -p ./.tmp/pg_data
podman compose up -d or docker compose up -d
```

Note it may be necessary on the first run to edit the context defined in docker-compose.yml

```context: ../../infrastructure/images/postgres```

### Setting up the local DynamoDB tables

Before running the load steps of the pipeline locally, you will need to create the DynamoDB tables locally.
This can be done using the `ftrs-aws-local reset` command.

## Create the local DynamoDB tables

### Pre-requisites

-Ensure you have the `ftrs-aws-local` package installed.Follow Instructions in the **Installation** section above.
-Ensure you have the AWS CLI installed and configured with the correct credentials.
-Run the below commands from the root of the **ftrs-aws-local** directory.

```bash
ftrs-aws-local reset \
    --init \
    --env local \
    --endpoint-url http://localhost:8000
```

The script can be aborted at the first prompt.

### Clearing Down DynamoDB Tables

To clear down the DynamoDB tables locally, you can delete them using NoSQL Workbench or the AWS CLI.

For deployed environments, you can use the `ftrs-aws-local reset` command to delete data within the existing tables.

## To delete all local DynamoDB tables use the command without the `--init` flag

```bash
ftrs-aws-local reset \
    --env local \
    --endpoint-url http://localhost:8000
```

## Delete the development DynamoDB data

```bash
ftrs-aws-local reset --env dev
```

## Delete a workspace development DynamoDB table

```bash
ftrs-aws-local reset --env dev --workspace my-workspace
```

## To load the local data clone

To load the local data clone, you will need to have the Postgres database running and the data dump file available.
Follow the steps from services/data-migration/README.md to extract, transform and load the data dump into your local
dynamoDB instance.

## Testing

Unit tests are run using Pytest. You can use the make target to conveniently run these tests, or run them directly using pytest.

```bash
eval $(poetry env activate)
pytest tests/unit
```
