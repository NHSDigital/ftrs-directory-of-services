# Account-Wide Infrastructure

Infrastructure that is deployed once per AWS account.

> Note: Deploy this stack using the `default` workspace.

This stack provisions:

1. IAM role for GitHub Actions (via OIDC)
2. Account-wide VPC, including public, private, and database subnets
3. A performance EC2 host for Apache `JMeter`–based testing

---

## Performance EC2 (Apache `JMeter`)

A single Amazon Linux 2023 EC2 instance in a private `subnet` for performance testing. Access is through AWS Systems Manager Session Manager (no inbound SSH). On first boot, user data installs Java, Apache `JMeter`, a minimal plugin set, an optional JWT library, and a convenience wrapper.

### What this stack creates

- EC2 instance in the first private `subnet` of the account-wide VPC
- Dedicated security group with minimal egress
  - TCP 443 to 0.0.0.0/0 (HTTPS)
  - UDP 53 to the VPC Route 53 Resolver only (CIDR: `${cidrhost(var.vpc["cidr"], 2)}/32`) (DNS)
- Dedicated NACLs with minimal DNS allowances (because NACLs are stateless)
  - Outbound UDP 53 to the VPC resolver (`${cidrhost(var.vpc["cidr"], 2)}/32`)
  - Inbound UDP 1024–65535 from the VPC resolver (`${cidrhost(var.vpc["cidr"], 2)}/32`)
- IAM role and instance profile attached to the instance
  - Managed policy: `AmazonSSMManagedInstanceCore`
- On first boot, user data installs:
  - Java 17 (`Amazon Corretto` with OpenJDK fallback) and base tools
  - Apache `JMeter` (from archive.apache.org) under `/opt/jmeter/current`
  - Apache `JMeter` Plugin Manager 1.11 and `cmdrunner` 2.3
  - Default plugins: `jpgc-graphs-basic` and `jpgc-graphs-additional`
  - JWT library JAR (version configurable)
  - Symlinks: `/usr/local/bin/jmeter` and `/usr/local/bin/jmeter-server`
  - Wrapper: `/usr/local/bin/jmeter-run`
  - SSM Agent installed and enabled (falls back to regional S3 RPM if needed)
  - Logs written to `/var/log/user-data.log`

### Variables (selected)

- `performance_instance_type` (string, default `t3.small`)
- `performance_volume_size` (number, default `30`; must be ≥ 30 GiB)
- `performance_version` (string, Apache `JMeter` version, default `5.6.3`)
- `performance_poweroff_after_setup` (true/false, default `true`) — power off after install to avoid idle cost
- `performance_ami_name_pattern` (list(string), default `['al2023-ami-*-x86_64']`)
- `performance_ami_architectures` (list(string), default `['x86_64']`)
- `performance_jwt_dependency_version` (string, default `4.5.0`)

Set these in your environment tfvars, for example `infrastructure/environments/dev/account_wide.tfvars`.

### Prerequisites

- Outbound internet access from private subnets (typically via a NAT Gateway) so the instance can download Apache `JMeter`, plugins, and the JWT JAR
- Alternatively, configure VPC interface endpoints for SSM/SSMMessages/EC2Messages if operating without NAT
- The account-level GitHub runner role needs permission to create and pass the instance role/profile (configured centrally in this repository)

### Usage

- Plan and apply this stack with the account-wide tfvars and your environment tfvars
- After apply, connect using Session Manager from the AWS Console or CLI
- Validate installation on the instance:
  - Run `jmeter -v` or execute tests with `jmeter-run` as needed
  - Inspect `/var/log/user-data.log` for provisioning details

### Outputs

- `performance_instance_id`
- `performance_private_ip`
- `performance_security_group_id`

### Troubleshooting

- If Apache `JMeter`, plugins, or the JWT JAR are missing, check `/var/log/user-data.log` and confirm outbound access
- Confirm the SSM Agent is running: `systemctl status amazon-ssm-agent`
- `JAVA_HOME` and `JMETER_HOME` are exported in profile scripts; the `jmeter-run` wrapper also sets them if missing
