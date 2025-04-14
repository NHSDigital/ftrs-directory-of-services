# Find the right service infrastructure

## Table of Contents

- [Find the right service infrastructure](#find-the-right-service-infrastructure)
  - [Table of Contents](#table-of-contents)
  - [Resource naming conventions](#resource-naming-conventions)
    - [Account wide resources](#account-wide-resources)
    - [Application resources](#application-resources)

## Resource naming conventions

We have introduced some naming conventions to

- identify the project that owns the resources
- trace resources back to the IAC that built those resources
- identify account wide resources
- identify the environment for which the resources were built
- identify the workspace in which the resources have been built

### Account wide resources

Some infrastructure we expect to build once per AWS account/environment. Currently these account-wide resources are

- the VPC/VPN,
- terraform management resources and
- the github runner

The names for these resources is linked to the name of the gihub repository (eg ftrs-directory-of-services)

The convention for naming account wide infrastructure is

- the name of the repository
- the environment for which they are built
- the unique name of the resource

For example a vpc built from this repo for the dev environment would be `ftrs-directory-of-services-dev-my-vpc`

The `account_prefix` variable has been created to simplify resource naming by concatenating the name of the repository and environment
See ftrs-directory-of-services/infrastructure/common/locals.tf

### Application resources

The resources built specifically for business user cases are named slightly differently and should follow this convention.

- the owning project - ie ftrs-dos
- the environment for which they are built - eg dev/test/prod etc
- the stack that holds the terraform code - eg database or data_migration
- the unique name of the resource - eg my_bucket
- the terraform workspace (if not the default workspace)

For example an S3 bucket called `demo-bucket` defined in the `my_bucket` stack and built in the dev environment for the default workspace would be named `ftrs-dos-dev-my-bucket-demo-bucket`. The corresponding bucket built in the `fdos-000` workspace would be `ftrs-dos-dev-my-bucket-demo-bucket-fdos-000`

