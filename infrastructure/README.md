# Infrastructure

Terraform infrastructure as code for the Find the Right Service platform.

## Table of Contents

- [Infrastructure](#infrastructure)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Structure](#structure)
  - [Stacks](#stacks)
  - [Modules](#modules)
  - [Environments](#environments)
  - [Resource Naming Conventions](#resource-naming-conventions)
    - [Account-Wide Resources](#account-wide-resources)
    - [Application Resources](#application-resources)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Deploying a Stack](#deploying-a-stack)
    - [Common Commands](#common-commands)

## Overview

This directory contains all Terraform configurations for deploying and managing FtRS infrastructure across multiple AWS environments. The infrastructure follows a modular approach with reusable components and environment-specific configurations.

## Structure

```text
infrastructure/
├── common/           # Shared Terraform configuration (providers, locals)
├── environments/     # Environment-specific variable files
├── modules/          # Reusable Terraform modules
├── stacks/           # Deployable infrastructure stacks
├── toggles/          # Feature toggle configurations
└── *.tfvars          # Stack-specific variable files
```

## Stacks

Deployable infrastructure components organised by functional area:

- **account_policies**: AWS account-level policies and configurations
- **`account_security`**: Security controls and compliance configurations
- **`account_wide`**: VPC, networking, and shared account resources
- **app_config**: AWS AppConfig for feature toggles and configuration
- **`artefact_management`**: S3 buckets for build artifacts and deployments
- **`athena`**: Athena workgroups and query configurations
- **crud_apis**: Infrastructure for internal CRUD API services
- **`data_migration`**: Resources for data migration processes
- **database**: DynamoDB tables and database configurations
- **`domain_name`**: Route53 domains and DNS configurations
- **dos_search**: DoS Search API infrastructure and monitoring
- **etl_ods**: ETL pipeline infrastructure for ODS data processing
- **github_runner**: Self-hosted GitHub Actions runners
- **is_performance**: Performance testing infrastructure
- **opensearch**: OpenSearch clusters and ingestion pipelines
- **read_only_viewer**: Read-only viewer application infrastructure
- **slack_notifier**: Centralised Slack notification service
- **terraform_management**: Terraform state management (S3, DynamoDB)
- **ui**: Frontend application infrastructure

Each stack has its own directory under `stacks/` with corresponding `.tfvars` file at the root.

[View detailed monitoring documentation](MONITORING.md)

## Modules

Reusable Terraform modules for common infrastructure patterns:

- **`acm`**: AWS Certificate Manager certificates
- **api-gateway-rest**: REST API Gateway configurations
- **api-gateway-v2-http**: HTTP API Gateway configurations
- **app-config**: AppConfig applications and environments
- **cloudwatch-alarm**: Individual CloudWatch alarm creation
- **cloudwatch-monitoring**: Complete monitoring solution with templates
- **`dynamodb`**: DynamoDB table configurations
- **kms**: KMS key management
- **lambda**: Lambda function deployments
- **ods-mock-api**: Mock ODS API for testing
- **route-53**: Route53 DNS configurations
- **s3**: S3 bucket configurations
- **shield**: AWS Shield protection
- **slack-notifications**: Slack notification Lambda integration
- **sns**: SNS topic configurations

[View monitoring modules documentation](modules/MONITORING.md)

## Environments

Environment-specific configurations stored in `environments/`:

- **dev**: Development environment
- **int**: Integration environment
- **test**: Testing environment
- **ref**: Reference environment
- **sandpit**: Experimental/sandbox environment
- **prod**: Production environment
- **non-prod**: Non-production shared resources
- **mgmt**: Management/tooling environment

Each environment directory contains `.tfvars` files for each stack with environment-specific values.

## Resource Naming Conventions

### Account-Wide Resources

Resources built once per AWS account/environment (VPC, Terraform state):

**Format**: `{repository-name}-{environment}-{resource-name}`

**Example**: `ftrs-directory-of-services-dev-my-vpc`

The `account_prefix` variable simplifies naming by concatenating repository name and environment.

**Exceptions**:

- GitHub runner stack: Uses repository name only (no environment)
- Terraform management stack: Unchanged naming

### Application Resources

Resources for specific business use cases:

**Format**: `{project}-{environment}-{stack}-{resource-name}[-{workspace}]`

**Examples**:

- Default workspace: `ftrs-dos-test-demo-example`
- Named workspace: `ftrs-dos-test-demo-example-ftrs-000`

The `resource_prefix` variable simplifies naming by concatenating project, environment, and stack.

**Components**:

- **project**: `ftrs-dos`
- **environment**: `dev`, `test`, `prod`, etc.
- **stack**: `database`, `dos_search`, etc.
- **resource-name**: Unique identifier for the resource
- **workspace**: Optional Terraform workspace suffix

See `infrastructure/common/locals.tf` for variable definitions.

## Getting Started

### Prerequisites

- Terraform (version specified in `common/versions.tf`)
- AWS CLI configured with appropriate credentials
- Access to the target AWS account

### Deploying a Stack

1. Navigate to the stack directory:

   ```bash
   cd infrastructure/stacks/{stack_name}
   ```

2. Initialize Terraform:

   ```bash
   terraform init
   ```

3. Select workspace (if applicable):

   ```bash
   terraform workspace select {workspace_name}
   ```

4. Plan changes:

   ```bash
   terraform plan -var-file=../../environments/{env}/{stack_name}.tfvars
   ```

5. Apply changes:

   ```bash
   terraform apply -var-file=../../environments/{env}/{stack_name}.tfvars
   ```

### Common Commands

```bash
# List workspaces
terraform workspace list

# Show current state
terraform show

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive
```
