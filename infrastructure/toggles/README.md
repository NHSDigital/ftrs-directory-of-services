# Feature Toggle Management

This directory contains the centralized feature toggle registry for the FTRS Directory of Services application. Feature toggles (also known as feature flags) enable controlled rollout of features across different environments without requiring code deployments.

## Table of Contents

- [Overview](#overview)
- [Toggle Types](#toggle-types)
  - [AppConfig Flags](#appconfig-flags)
  - [Stack Toggles](#stack-toggles)
  - [API Gateway Toggles](#api-gateway-toggles)
- [Flag Naming Convention](#flag-naming-convention)
- [Toggle Registry Structure](#toggle-registry-structure)
- [Governance Process](#governance-process)
  - [Adding a New Toggle](#adding-a-new-toggle)
  - [Modifying an Existing Toggle](#modifying-an-existing-toggle)
  - [Retiring a Toggle](#retiring-a-toggle)
- [Usage Guidelines](#usage-guidelines)
  - [Best Practices](#best-practices)
  - [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Environment Configuration](#environment-configuration)
  - [Stack Toggle Workflow Integration](#stack-toggle-workflow-integration)
  - [Troubleshooting Stack Toggles](#troubleshooting-stack-toggles)
  - [Environment Hierarchy](#environment-hierarchy)
  - [Typical Rollout Pattern](#typical-rollout-pattern)
  - [Emergency Toggle Changes](#emergency-toggle-changes)

## Overview

The toggle system provides three distinct types of toggles:

1. **AppConfig Flags**: Runtime feature toggles stored in AWS AppConfig
2. **Stack Toggles**: Infrastructure-level toggles that control Terraform stack deployment
3. **API Gateway Toggles**: Endpoint-level toggles that control API route availability

All toggles are defined in the [toggle-registry.yaml](toggle-registry.yaml) file, which serves as the single source of truth for feature toggles across the application.

## Toggle Types

### AppConfig Flags

AppConfig flags are runtime toggles that control application behavior without requiring redeployment. These are stored in AWS AppConfig and can be modified dynamically.

**Use Cases:**

- Enable/disable data migration processes
- Control feature availability in application logic
- Implement gradual feature rollouts

**Example:**

```yaml
- id: data_migration_organisation_enabled
  name: "Data Migration - Organisation Enabled"
  description: "Enable the migration of Organisation (+ Endpoint) resources from the current DoS"
  service: data-migration
  owner: "Data Migration Team"
```

### Stack Toggles

Stack toggles control whether entire infrastructure stacks are deployed via Terraform. These are infrastructure-level decisions that affect environment provisioning.

**Use Cases:**

- Enable/disable OpenSearch deployment
- Control UI stack deployment
- Manage infrastructure cost optimization

**Example:**

```yaml
- id: stack_opensearch_enabled
  name: "OpenSearch Stack Enabled"
  description: "Enable/disable OpenSearch stack deployment"
  terraform_variable: opensearch_stack_enabled
  stack_path: infrastructure/stacks/opensearch
  owner: "Infrastructure Team"
  environments:
    workspace: true
    dev: true
    test: true
    int: false
    ref: false
    sandpit: false
    prod: false
```

**How Stack Toggles Work:**

1. **Toggle Registry Definition**: Stack toggles are defined in `toggle-registry.yaml` with environment-specific values
2. **Tfvars Generation**: The `scripts/workflow/generate-stack-toggles.py` script reads the registry and generates `stacks.workspace.auto.tfvars` for the current workspace
3. **Terraform Consumption**: Each stack has a `{stack_name}_stack_enabled` variable that controls resource deployment via `count` meta-argument
4. **Resource Creation**: When `stack_enabled = false`, zero resources are created (count = 0)
5. **Automation**: Stack toggle generation is automatically triggered via the `scripts/workflow/generate-stack-toggles.sh` wrapper script during CI/CD pipelines

**Using Stack Toggles:**

The stack toggle generation script is located at `scripts/workflow/generate-stack-toggles.py`. To manually generate or update stack toggles:

```bash
# Generate stack toggles for current workspace
./scripts/workflow/generate-stack-toggles.sh

# Or run the Python script directly
python3 scripts/workflow/generate-stack-toggles.py

# Dry-run to see what would be generated (if supported)
python3 scripts/workflow/generate-stack-toggles.py --dry-run
```

The script will create/update `infrastructure/toggles/stacks.workspace.auto.tfvars` with the appropriate toggle values based on your current environment configuration.

**Stack Toggle Implementation:**

Each stack implementing toggles must follow these conventions:

1. **Variable Definition**: Add a `{stack_name}_stack_enabled` boolean variable with default `true` in `variables.tf`
2. **Local Variable**: Create a `locals.tf` with `stack_enabled = var.{stack_name}_stack_enabled ? 1 : 0`
3. **Resource Count**: Add `count = local.stack_enabled` to all root-level resources and modules
4. **Resource References**: Update all resource references to use index `[0]` (e.g., `module.example[0].id`)
5. **Output Conditionals**: Update outputs to handle disabled state with conditionals
6. **Registry Entry**: Add the toggle to `toggle-registry.yaml` under `stack_toggles` section with appropriate environment settings

**Toggle Generation Output:**

When you run the stack toggle generation script, it creates/updates:

- `infrastructure/toggles/stacks.workspace.auto.tfvars` - Contains boolean values for each stack toggle based on the current workspace configuration

This tfvars file is automatically loaded by Terraform when you run commands in any stack directory.

**Example Stack Implementation:**

```terraform
# variables.tf
variable "opensearch_stack_enabled" {
  description = "Enable or disable the opensearch stack"
  type        = bool
  default     = true
}

# locals.tf
locals {
  stack_enabled = var.opensearch_stack_enabled ? 1 : 0
}

# s3.tf
module "s3" {
  count = local.stack_enabled
  source = "../../modules/s3"
  # ... other arguments
}

# Other resource referencing the module
resource "aws_s3_bucket_policy" "policy" {
  count = local.stack_enabled
  bucket = module.s3[0].s3_bucket_id
  # ... other arguments
}

# outputs.tf
output "bucket_name" {
  value = local.stack_enabled == 1 ? module.s3[0].s3_bucket_name : ""
}
```

**Cost Impact:**

Disabling a stack results in:

- Zero AWS resources provisioned
- Zero ongoing AWS costs for that stack
- Faster Terraform apply times
- Reduced blast radius for changes

**Available Stack Toggles:**

The following stacks can be enabled/disabled via toggles:

| Stack | Terraform Variable | Stack Path | Purpose |
|-------|-------------------|------------|---------|
| opensearch | `opensearch_stack_enabled` | `infrastructure/stacks/opensearch` | OpenSearch Serverless collection and ingestion pipeline |
| read_only_viewer | `read_only_viewer_stack_enabled` | `infrastructure/stacks/read-only-viewer` | Read-only viewer frontend application |
| ui | `ui_stack_enabled` | `infrastructure/stacks/ui` | Main UI application with authentication |

**Adding a New Stack Toggle:**

To add a new stack toggle:

1. Add the toggle definition to `infrastructure/toggles/toggle-registry.yaml` under the `stack_toggles` section
2. Define environment-specific values (true/false for each environment)
3. Run `./scripts/workflow/generate-stack-toggles.sh` to regenerate the tfvars file
4. Implement the toggle in your stack following the Stack Toggle Implementation pattern above
5. Test in lower environments before enabling in production

### API Gateway Toggles

API Gateway toggles control the availability of specific API endpoints. When disabled, these endpoints return a configured error response (typically 503 Service Unavailable).

**Use Cases:**

- Enable/disable CRUD operations per resource type
- Control search endpoint availability
- Implement maintenance mode for specific endpoints

**Example:**

```yaml
- id: dos_search_organisation_search_enabled
  name: "DoS Search - Organisation Search Enabled"
  description: "Enable/disable the DoS Search Organisation endpoint (Search by ODS Code)"
  route: "GET /Organization"
  service: dos-search
  terraform_variable: dos_search_organisation_search_enabled
  disabled_response:
    status_code: 503
    message: "Organisation search endpoint is currently disabled"
```

## Flag Naming Convention

All feature flag names MUST follow the standardized naming convention to ensure consistency and discoverability across the platform.

### Format

```text
{service}_{feature}_{qualifier}
```

### Rules

1. **Use lowercase with underscores (snake_case)**
   - Correct: `dos_search_organisation_enabled`
   - Incorrect: `dosSearchOrganisationEnabled`, `DoS-Search-Organisation-Enabled`

2. **Start with the service name**
   - Service names: `data_migration`, `dos_search`, `crud_api`, `etl_ods`, `stack`
   - Must match the service name in the repository structure except stack

3. **Include a clear feature descriptor**
   - Describe what functionality is being toggled
   - Examples: `organisation`, `location`, `healthcareservice`, `opensearch`

4. **End with a qualifier**
   - Common qualifiers: `enabled`, `create_enabled`, `read_enabled`, `update_enabled`, `delete_enabled`
   - Use `enabled` for simple on/off toggles

5. **Avoid abbreviations except well-known ones**
   - Acceptable: `ODS`, `API`, `CRUD`, `UI`
   - Use full names for clarity: `organisation` not `org`, `healthcare` not `hc`

### Examples

**Valid Names:**

- `data_migration_organisation_enabled`
- `dos_search_organisation_search_enabled`
- `crud_api_location_create_enabled`
- `stack_opensearch_enabled`
- `etl_ods_gp_practice_sync_enabled`

**Invalid Names:**

- `orgSearch` (camelCase, abbreviated)
- `dos-search-enabled` (hyphens)
- `SEARCH_ORG` (uppercase)
- `toggle_organisation` (missing service prefix)
- `dos_org_enabled` (unapproved abbreviation)

## Toggle Registry Structure

The toggle system uses the following files:

- **`toggle-registry.yaml`**: Central registry containing all toggle definitions
- **`stacks.workspace.auto.tfvars`**: Auto-generated tfvars file containing stack toggle values for the current workspace
- **`scripts/workflow/generate-stack-toggles.py`**: Python script that reads the registry and generates tfvars
- **`scripts/workflow/generate-stack-toggles.sh`**: Shell wrapper for the Python generation script

The [toggle-registry.yaml](toggle-registry.yaml) file is organized into three main sections:

```yaml
appconfig_flags:
  - id: {toggle_id}
    name: "{Human Readable Name}"
    description: "{Detailed description of toggle purpose}"
    service: {service-name}
    owner: "{Team Name}"
    environments:
      workspace: true|false
      dev: true|false
      test: true|false
      int: true|false
      ref: true|false
      sandpit: true|false
      prod: true|false

stack_toggles:
  - id: {toggle_id}
    name: "{Human Readable Name}"
    description: "{Detailed description of toggle purpose}"
    terraform_variable: {variable_name}
    stack_path: {path_to_stack}
    owner: "{Team Name}"
    environments: {...}

api_gateway_toggles:
  - id: {toggle_id}
    name: "{Human Readable Name}"
    description: "{Detailed description of toggle purpose}"
    route: "{HTTP_METHOD /path}"
    service: {service-name}
    terraform_variable: {variable_name}
    disabled_response:
      status_code: {http_code}
      message: "{error_message}"
    owner: "{Team Name}"
    environments: {...}
```

## Governance Process

### Adding a New Toggle

1. **Identify the Need**
   - Clearly define what feature or functionality requires a toggle
   - Determine the appropriate toggle type (AppConfig, Stack, or API Gateway)
   - Identify which environments need the toggle

2. **Name the Toggle**
   - Follow the [Flag Naming Convention](#flag-naming-convention)
   - Ensure the name is unique and descriptive
   - Verify it doesn't conflict with existing toggles

3. **Document the Toggle**
   - Create a comprehensive description explaining the toggle's purpose
   - Identify the owning team
   - Define the default state for each environment

4. **Create a Pull Request**
   - Add the toggle definition to [toggle-registry.yaml](toggle-registry.yaml)
   - Include the rationale and use case in the PR description
   - Follow the commit message guidelines (Conventional Commits)
   - Example: `feat(toggles): Add organisation delete toggle for CRUD API`

5. **Review Process**
   - Technical review by at least two team member
   - Architecture review if the toggle affects infrastructure or cross-cutting concerns
   - Security review for toggles that control access or authentication

6. **Implementation**
   - Update relevant Terraform configurations to reference the new toggle
   - Update application code to check the toggle state
   - Add tests to verify toggle behavior in both enabled and disabled states
   - Update relevant documentation

7. **Deployment**
   - Deploy infrastructure changes (for Stack and API Gateway toggles)
   - Verify toggle functionality in lower environments before production
   - Document any manual steps required for toggle activation

### Modifying an Existing Toggle

1. **Environment Changes**
   - Changes to toggle states across environments require a PR
   - Include justification for environment-specific changes
   - Notify affected teams before changing production toggles

2. **Description Updates**
   - Keep descriptions current and accurate
   - Update if toggle behavior changes

3. **Ownership Changes**
   - Update the `owner` field when team ownership transfers
   - Ensure new owner is aware of toggle lifecycle

### Retiring a Toggle

Feature toggles should not live forever. Once a feature is fully rolled out and stable, consider removing the toggle to reduce technical debt.

#### When to Retire a Toggle

- Feature is enabled in all environments and no longer needs conditional control
- Feature has been stable in production for at least 3 months
- No rollback scenarios require the toggle
- Business stakeholders confirm feature is permanent

#### Retirement Process

1. **Create a Retirement Proposal**
   - Document the toggle to be retired
   - Verify it's enabled in all environments
   - Confirm with stakeholders that removal is acceptable
   - Create a Jira ticket to track the retirement

2. **Code Cleanup**
   - Remove all code that checks the toggle state
   - Simplify logic that was conditional on the toggle
   - Remove toggle-related configuration from infrastructure
   - Update tests to remove toggle-specific test cases

3. **Remove from Registry**
   - Delete the toggle definition from [toggle-registry.yaml](toggle-registry.yaml)
   - Create a PR with the changes
   - Example commit: `chore(toggles): Remove data_migration_organisation_enabled toggle`

4. **Verify Deployment**
   - Ensure successful deployment to all environments
   - Monitor for any unexpected behavior
   - Document the retirement date for audit purposes

5. **Update Documentation**
   - Remove references to the retired toggle from user guides
   - Update architecture diagrams if applicable

#### Retirement Timeline

- **Lower Environments (workspace, dev, test)**: Can be retired immediately after code cleanup
- **Higher Environments (int, ref, sandpit, prod)**: Requires notice and stakeholder approval

## Usage Guidelines

### Best Practices

1. **Keep Toggles Short-Lived**
   - Aim to retire toggles within 6-12 months of creation
   - Long-lived toggles become technical debt

2. **Use Descriptive Names**
   - Toggle names should clearly indicate their purpose
   - Follow the naming convention strictly

3. **Set Sensible Defaults**
   - Lower environments (workspace, dev, test) can be more permissive
   - Production defaults should be conservative (disabled by default for risky features)

4. **Document Toggle Dependencies**
   - If toggles depend on each other, document this clearly
   - Consider whether multiple toggles could be consolidated

5. **Test Both States**
   - Always test feature behavior when toggle is enabled
   - Always test feature behavior when toggle is disabled
   - Include toggle testing in automated test suites

6. **Monitor Toggle Usage**
   - Track which toggles are checked most frequently
   - Identify toggles that are always in the same state (candidates for retirement)

7. **Communicate Changes**
   - Notify relevant teams when changing toggle states
   - Use release notes to communicate toggle changes
   - Update runbooks with toggle information

### Anti-Patterns to Avoid

❌ **Don't** create toggles for every small change  
❌ **Don't** use toggles as a substitute for proper testing  
❌ **Don't** leave toggles enabled in production without monitoring  
❌ **Don't** create complex toggle dependencies  
❌ **Don't** use toggles for configuration values (use environment variables instead)  
❌ **Don't** forget to remove toggles after feature stabilization  

## Environment Configuration

Toggles can be configured per environment to support gradual rollouts and environment-specific requirements.

### Stack Toggle Workflow Integration

Stack toggles are automatically managed during the CI/CD pipeline:

1. **Local Development**: Run `./scripts/workflow/generate-stack-toggles.sh` before applying Terraform changes
2. **CI/CD Pipeline**: The generation script is executed automatically before Terraform plan/apply stages
3. **Environment Detection**: The script automatically determines the current workspace/environment
4. **File Generation**: Creates `stacks.workspace.auto.tfvars` with the appropriate toggle values

### Troubleshooting Stack Toggles

**Toggle not taking effect:**

- Verify the toggle is defined in `toggle-registry.yaml`
- Re-run `./scripts/workflow/generate-stack-toggles.sh`
- Check that `stacks.workspace.auto.tfvars` contains the expected value
- Ensure the stack's `variables.tf` defines the corresponding variable
- Verify `locals.tf` properly calculates `stack_enabled`

**Terraform errors with disabled stacks:**

- Ensure all resource references use `[0]` index when accessing counted resources
- Check that outputs handle the disabled state (local.stack_enabled == 0)
- Verify dependencies between resources respect the count meta-argument

**Stack unexpectedly disabled:**

- Check the environment-specific value in `toggle-registry.yaml`
- Verify the correct workspace is active (`terraform workspace show`)
- Regenerate the tfvars file to ensure it's up to date

### Environment Hierarchy

```text
workspace (local development)
  ↓
dev (development)
  ↓
test (testing)
  ↓
int (integration)
  ↓
ref (reference)
  ↓
sandpit (sandbox)
  ↓
prod (production)
```

### Typical Rollout Pattern

1. **Enable in workspace and dev**: Early development and unit testing
2. **Enable in test**: Integration testing and QA
3. **Enable in int**: Integration with external systems
4. **Enable in ref and sandpit**: Pre-production validation
5. **Enable in prod**: Production rollout

### Emergency Toggle Changes

In case of production incidents, toggles can be disabled quickly:

1. **API Gateway and Stack Toggles**: Require Terraform changes and deployment (15-30 minutes)
2. **AppConfig Flags**: Can be changed directly in AWS AppConfig (1-2 minutes)

For AppConfig flags, emergency changes should:

- Be communicated immediately to the team
- Be followed up with a PR to update the registry
- Be documented in incident reports

## Related Documentation

- [Terraform Configuration](../README.md)
- [Service Documentation](../../services/README.md)
- [Architecture Decision Records](../../architecture/README.md)

## Contact

For questions about the toggle system or to propose changes to this process, contact:

- **Platform Team**: For infrastructure and deployment questions
- **Service Teams**: For service-specific toggle questions
- **Architecture Team**: For governance and strategy questions
