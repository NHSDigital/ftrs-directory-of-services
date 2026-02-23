# Services

Directory containing the services that make up the FtRS suite.

## Table of Contents

- [Services](#services)
  - [Table of Contents](#table-of-contents)
  - [CRUD APIs](#crud-apis)
  - [Data Migration](#data-migration)
  - [DoS Search](#dos-search)
  - [DoS UI](#dos-ui)
  - [ETL ODS](#etl-ods)
  - [Read-Only Viewer](#read-only-viewer)
  - [Sandbox DoS Search](#sandbox-dos-search)
  - [Slack Notifier](#slack-notifier)

## CRUD APIs

Internal APIs for making CRUD updates to the data store. Currently includes the Organisation API for updating data in the Organisation table. Each API is organised as a subdirectory under `crud-apis/`.

[View CRUD APIs README](crud-apis/README.md)

## Data Migration

Service responsible for migrating data from the current live Directory of Services to the future Find the Right Service solution. Includes local OpenSearch configuration for testing and development.

[View Data Migration README](data-migration/README.md)

## DoS Search

FHIR-compliant API service for healthcare system integrations. Provides endpoints to search for Directory of Services (DoS) data by ODS code, returning organization and endpoint information in FHIR Bundle format. Includes monitoring, alerting, and Slack notifications.

[View DoS Search README](dos-search/README.md)

## DoS UI

React and TypeScript-based user interface for the Find the Right Service Directory of Services. Built with TanStack Router for routing and data fetching, and uses NHS.UK Frontend for styling.

[View DoS UI README](dos-ui/README.md)

## ETL ODS

ETL (Extract, Transform, Load) pipeline for processing Organisation Data Service (ODS) data. Includes extractor, transformer, and consumer components for ingesting and processing healthcare organization data.

[View ETL ODS README](etl-ods/README.md)

## Read-Only Viewer

Test utility for viewing and testing the Find the Right Service database. Allows users to view data and test available APIs in a read-only mode.

[View Read-Only Viewer README](read-only-viewer/README.md)

## Sandbox DoS Search

API sandbox serving canned responses for API Management (APIM) testing and development. Provides mock responses for DoS Search endpoints without requiring live backend services.

[View Sandbox DoS Search README](sandbox-dos-search/README.md)

## Slack Notifier

Reusable service for sending formatted CloudWatch alarm notifications to Slack channels. Processes alarm data from SNS topics and delivers rich, formatted messages with severity detection and AWS console links. Designed to support multiple alarm types across the platform.

[View Slack Notifier README](slack-notifier/README.md)
