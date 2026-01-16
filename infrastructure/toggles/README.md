# Feature Toggle Management

This directory contains the centralized feature toggle registry for the FTRS Directory of Services application. Feature toggles (also known as feature flags) enable controlled rollout of features across different environments without requiring code deployments.

## Table of Contents

- [Overview](#overview)
- [Toggle Types](#toggle-types)
- [Flag Naming Convention](#flag-naming-convention)
- [Toggle Registry Structure](#toggle-registry-structure)
- [Governance Process](#governance-process)
- [Usage Guidelines](#usage-guidelines)
- [Environment Configuration](#environment-configuration)

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
  terraform_variable: opensearch_enabled
  stack_path: infrastructure/stacks/opensearch
```

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
   - Common qualifiers: `enabled`, `disabled`, `create_enabled`, `read_enabled`, `update_enabled`, `delete_enabled`
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
