# Services

Directory containing the services that make up the FtRS suite.

Any new services should be added into this directory.

## Table of Contents

- [Services](#services)
  - [Table of Contents](#table-of-contents)
  - [Data Migration](#data-migration)
  - [Read-Only Viewer](#read-only-viewer)
  - [Opensearch ingestion pipelines](#opensearch-ingestion-pipelines)

## Data Migration

This service is responsible for the migration of data from the current live Directory of Services to the future Find the Right Service solution. More details can be found in the [README for the service](https://github.com/NHSDigital/ftrs-directory-of-services/blob/main/services/data-migration/README.md).

## Read-Only Viewer

The FtRS Read-Only Viewer is a test utility for the Find the Right Service database. It allows users to view the data in the database and test the APIs that are available. More details can be found in the [README for the service](https://github.com/NHSDigital/ftrs-directory-of-services/blob/main/services/read-only-viewer/README.md).

## Opensearch ingestion pipelines

A github workflow is scheduled to run at the end of the day (currently 18:00) and stop any active opensearch
ingestion pipelines in develop. This is to help keep costs down. If you need to restart an ingestion pipeline then

- assume a role in dev account
- identify name of ingestion pipeline to restart (via console or using script below)

```shell
aws osis list-pipelines --region "${AWS_REGION}" | jq -r '.Pipelines[] | .PipelineName, .Status'
```

- run following command to restart your chosen pipeline - eg organisation-fdos-222 - this will return the pipeline's new status - ie `STARTING`

```shell
aws osis start-pipeline --region "${AWS_REGION}" --pipeline-name organisation-fdos-222 | jq -r '.Pipeline | .Status'
```

- you can check via console or by re-running the list-pipelines command above to check the pipeline is restarting. Note it will take a few minutes to become `ACTIVE`
