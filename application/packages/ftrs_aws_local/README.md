### Start Database Container

For local development, this project relies on a local Postgres and local DynamoDB instance running in a docker container.
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
This can be done using the `dos-etl reset` command.

## Create the local DynamoDB tables
```bash
ftrs-aws-local reset \
    --init \
    --env local \
    --endpoint-url http://localhost:8000 \
```

The script can be aborted at the first prompt.

### Clearing Down DynamoDB Tables

To clear down the DynamoDB tables locally, you can delete them using NoSQL Workbench or the AWS CLI.

For deployed environments, you can use the `ftrs-aws-local reset` command to delete data within the existing tables.

## To delete all local DynamoDB tables use the command without the `--init` flag:

```bash
ftrs-aws-local reset \
    --env local \
    --endpoint-url http://localhost:8000
```

# Delete the dev DynamoDB data

```bash
ftrs-aws-local reset --env dev
```

# Delete a workspace dev DynamoDB table

```bash
ftrs-aws-local reset --env dev --workspace my-workspace
```

## To load the local data clone, you will need to have the Postgres database running and the data dump file available.
## Follow the steps from services/data-migration/README.md to extract, transform and load the data dump into your local dynamoDB instance.





