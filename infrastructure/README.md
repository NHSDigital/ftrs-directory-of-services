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

- the vpc, vpn
- Terraform management resources and

The names for these resources is linked to the name of the github repository (eg ftrs-directory-of-services)

The convention for naming account wide infrastructure is

- the name of the repository
- the environment for which they are built
- the unique name of the resource

For example a vpc built from this repository for the develop environment would be `ftrs-directory-of-services-dev-my-vpc`

The `account_prefix` variable has been created to simplify resource naming by concatenating the name of the repository and environment
See ftrs-directory-of-services/infrastructure/common/locals.tf

Note

- the github runner stack is an exception to that rule and the name is based on the repository name (ie minus the environment)
- the Terraform management stack is also an exception to the rule remaining unchanged

Both these stacks could be brought into line later - but consideration would have to given to the configure-credentials action (passing an environment) and how to transfer state between buckets and lock tables etc

### Application resources

The resources built specifically for business user cases are named slightly differently and should follow this convention.

- the owning project - ie ftrs-dos
- the environment for which they are built - eg dev/test/prod etc
- the stack that holds the Terraform code - eg database
- the unique name of the resource - eg example
- the Terraform workspace (if not the default workspace)

For example an S3 bucket called `example` defined in the `demo` stack and built in the test environment for the default workspace would be named `ftrs-dos-test-demo-example`. The corresponding bucket built in the `fdos-000` workspace would be `ftrs-dos-test-demo-example-fdos-000`
