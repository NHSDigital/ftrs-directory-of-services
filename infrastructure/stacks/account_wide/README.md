# Account-Wide Infrastructure

This is infrastructure that should only be deployed once per account.

> **Note**: This should be deployed using the `default` workspace.

Currently, the following resources are deployed:

1. IAM role for GitHub Actions (via OIDC)
2. Account wide VPC including public, private and database subnets
