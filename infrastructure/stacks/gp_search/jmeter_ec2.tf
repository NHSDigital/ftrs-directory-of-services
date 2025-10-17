// JMeter EC2 instance(s) for performance testing
// Creates a small Amazon Linux 2023 instance in a private subnet, reachable via VPN over SSH.
// Installs Apache JMeter on first boot and powers off the instance when installation completes.

locals {
  jmeter_name = "${local.resource_prefix}-jmeter${local.workspace_suffix}"
}

# Use latest Amazon Linux 2023 AMI (x86_64)
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

# Security group to allow SSH from VPN only and limit egress to web
resource "aws_security_group" "jmeter_ec2_sg" {
  name        = "${local.jmeter_name}-sg"
  description = "JMeter EC2 security group (SSH from VPN only)"
  vpc_id      = data.aws_vpc.vpc.id
}

# Allow SSH from the VPN security group (dev only where VPN exists)
data "aws_security_group" "vpn_security_group" {
  count = var.environment == "dev" ? 1 : 0
  name  = "${local.account_prefix}-vpn-sg"
}

resource "aws_vpc_security_group_ingress_rule" "ssh_from_vpn" {
  count                        = var.environment == "dev" ? 1 : 0
  security_group_id            = aws_security_group.jmeter_ec2_sg.id
  referenced_security_group_id = data.aws_security_group.vpn_security_group[0].id
  description                  = "Allow SSH from VPN"
  ip_protocol                  = "tcp"
  from_port                    = 22
  to_port                      = 22
}

# Egress for package installs and test traffic (HTTPS and HTTP)
# trivy:ignore:aws-vpc-no-public-egress-sgr : JMeter host requires outbound 80/443 to the internet for package and plugin downloads and to reach external test endpoints. Traffic egresses via NAT/VPC endpoints where present.
# tfsec:ignore:aws-vpc-no-public-egress-sgr -- JMeter host requires outbound 80/443 to the internet for package and plugin downloads and to reach external test endpoints. Restricting to specific CIDRs is not feasible; traffic still routes via private subnets/NAT or VPC endpoints where present.
resource "aws_vpc_security_group_egress_rule" "egress_https" {
  security_group_id = aws_security_group.jmeter_ec2_sg.id
  description       = "Allow HTTPS egress"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}

# trivy:ignore:aws-vpc-no-public-egress-sgr : See justification above for HTTPS; HTTP is used for some mirrors/tools. Prefer HTTPS where possible.
# tfsec:ignore:aws-vpc-no-public-egress-sgr -- See justification above for HTTPS; HTTP is used for some mirrors/tools. Prefer HTTPS where possible.
resource "aws_vpc_security_group_egress_rule" "egress_http" {
  security_group_id = aws_security_group.jmeter_ec2_sg.id
  description       = "Allow HTTP egress"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}

# DNS resolution is required for SSM agent to reach regional endpoints
# trivy:ignore:aws-vpc-no-public-egress-sgr : DNS egress to 53/udp is required; resolution targets vary and cannot be feasibly enumerated. Traffic egresses via NAT.
resource "aws_vpc_security_group_egress_rule" "egress_dns_udp" {
  security_group_id = aws_security_group.jmeter_ec2_sg.id
  description       = "Allow DNS egress (UDP 53)"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "udp"
  from_port         = 53
  to_port           = 53
}

# Time sync helps avoid TLS/session issues with SSM
# trivy:ignore:aws-vpc-no-public-egress-sgr : NTP egress to 123/udp is required for accurate timekeeping; upstream targets vary and are typically AWS/NTP pools via NAT.
resource "aws_vpc_security_group_egress_rule" "egress_ntp_udp" {
  security_group_id = aws_security_group.jmeter_ec2_sg.id
  description       = "Allow NTP egress (UDP 123)"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "udp"
  from_port         = 123
  to_port           = 123
}

# IAM: support either an existing instance profile (if provided) or create one when allowed
resource "aws_iam_role" "jmeter_ec2_role" {
  count = (var.jmeter_instance_profile_name == "" && var.allow_create_iam) ? 1 : 0
  name  = "${local.jmeter_name}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
  permissions_boundary = var.permissions_boundary_arn != "" ? var.permissions_boundary_arn : null
  depends_on = [
    aws_iam_role_policy.app_runner_jmeter_iam_bootstrap,
    null_resource.iam_policy_propagation_wait
  ]
}

# Optional inline policy: S3 read and/or KMS decrypt
resource "aws_iam_role_policy" "jmeter_extra_access" {
  count = (var.jmeter_instance_profile_name == "" && var.allow_create_iam && (var.attach_s3_read || length(var.kms_key_arns) > 0)) ? 1 : 0
  name  = "${local.jmeter_name}-extra-access"
  role  = aws_iam_role.jmeter_ec2_role[0].name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = concat(
      var.attach_s3_read && length(var.s3_read_bucket_arns) > 0 ? [
        {
          Sid      = "S3ListBuckets",
          Effect   = "Allow",
          Action   = ["s3:ListBucket"],
          Resource = var.s3_read_bucket_arns
        },
        {
          Sid      = "S3GetObjects",
          Effect   = "Allow",
          Action   = ["s3:GetObject"],
          Resource = [for b in var.s3_read_bucket_arns : "${b}/*"]
        }
      ] : [],
      length(var.kms_key_arns) > 0 ? [
        {
          Sid      = "KMSDecrypt",
          Effect   = "Allow",
          Action   = ["kms:Decrypt"],
          Resource = var.kms_key_arns
        }
      ] : []
    )
  })
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  count      = (var.jmeter_instance_profile_name == "" && var.allow_create_iam) ? 1 : 0
  role       = aws_iam_role.jmeter_ec2_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "jmeter_ec2_profile" {
  count = (var.jmeter_instance_profile_name == "" && var.allow_create_iam) ? 1 : 0
  name  = "${local.jmeter_name}-instance-profile"
  role  = aws_iam_role.jmeter_ec2_role[0].name
  depends_on = [
    aws_iam_role_policy.app_runner_jmeter_iam_bootstrap,
    null_resource.iam_policy_propagation_wait
  ]
}

# Use an existing instance profile if provided
data "aws_iam_instance_profile" "existing" {
  count = var.jmeter_instance_profile_name != "" ? 1 : 0
  name  = var.jmeter_instance_profile_name
}

# Compute the effective instance profile name to attach to EC2
locals {
  created_instance_profile_name          = length(aws_iam_instance_profile.jmeter_ec2_profile) > 0 ? aws_iam_instance_profile.jmeter_ec2_profile[0].name : null
  existing_instance_profile_name         = length(data.aws_iam_instance_profile.existing) > 0 ? data.aws_iam_instance_profile.existing[0].name : null
  jmeter_effective_instance_profile_name = coalesce(local.existing_instance_profile_name, local.created_instance_profile_name)
}

# Pick a private subnet (first one)
locals {
  jmeter_subnet_id = element(data.aws_subnets.private_subnets.ids, 0)
}

# User data to install Java 17 and Apache JMeter, then power off the instance
locals {
  jmeter_user_data = <<-EOT
#!/usr/bin/env bash
set -euxo pipefail

exec > >(tee -a /var/log/user-data.log) 2>&1

REGION="eu-west-2"

echo "[user-data] Updating packages"
if command -v dnf >/dev/null 2>&1; then
  dnf -y update || true
elif command -v yum >/dev/null 2>&1; then
  yum -y update || true
fi

echo "[user-data] Installing Java 17 (Amazon Corretto) and utilities"
if command -v dnf >/dev/null 2>&1; then
  dnf -y install java-17-amazon-corretto-headless unzip jq curl wget tar || true
else
  yum -y install java-17-amazon-corretto-headless unzip jq curl wget tar || true
fi

# Ensure SSM Agent is present and running so Session Manager works
# Try repo first; if missing, fall back to the regional S3 RPM for AL2023
echo "[user-data] Ensuring SSM Agent installed and running"
if command -v dnf >/dev/null 2>&1; then
  dnf -y install amazon-ssm-agent || true
elif command -v yum >/dev/null 2>&1; then
  yum -y install amazon-ssm-agent || true
fi
if ! rpm -q amazon-ssm-agent >/dev/null 2>&1; then
  echo "[user-data] Installing SSM Agent from S3 fallback"
  rpm -Uvh --force "https://s3.$${REGION}.amazonaws.com/amazon-ssm-$${REGION}/latest/linux_amd64/amazon-ssm-agent.rpm"
fi
systemctl enable amazon-ssm-agent
systemctl restart amazon-ssm-agent
sleep 8
systemctl is-active --quiet amazon-ssm-agent || (systemctl status amazon-ssm-agent --no-pager || true)
amazon-ssm-agent -version || true

JMETER_VERSION="${var.jmeter_version}"
JMETER_TGZ="apache-jmeter-$${JMETER_VERSION}.tgz"
JMETER_URL="https://archive.apache.org/dist/jmeter/binaries/$${JMETER_TGZ}"

echo "[user-data] Creating install dirs"
install -d -m 0755 /opt /opt/jmeter

echo "[user-data] Downloading Apache JMeter $${JMETER_VERSION}"
cd /opt
curl -fL -o "$${JMETER_TGZ}" "$${JMETER_URL}"

echo "[user-data] Extracting JMeter"
tar -xzf "$${JMETER_TGZ}"
rm -f "$${JMETER_TGZ}"

if [ -d "/opt/apache-jmeter-$${JMETER_VERSION}" ]; then
  mv "/opt/apache-jmeter-$${JMETER_VERSION}" /opt/jmeter/apache-jmeter
fi

ln -sf /opt/jmeter/apache-jmeter/bin/jmeter /usr/local/bin/jmeter
ln -sf /opt/jmeter/apache-jmeter/bin/jmeter-server /usr/local/bin/jmeter-server

# Install JMeter Plugin Manager, cmdrunner, and common plugins
JMETER_HOME=/opt/jmeter/apache-jmeter
PLUGINS_MANAGER_VERSION=1.11
CMDRUNNER_VERSION=2.3
echo "[user-data] Installing JMeter Plugin Manager $${PLUGINS_MANAGER_VERSION} and cmdrunner $${CMDRUNNER_VERSION}"
curl -fL -o "$${JMETER_HOME}/lib/ext/jmeter-plugins-manager-$${PLUGINS_MANAGER_VERSION}.jar" \
  "https://repo1.maven.org/maven2/kg/apc/jmeter-plugins-manager/$${PLUGINS_MANAGER_VERSION}/jmeter-plugins-manager-$${PLUGINS_MANAGER_VERSION}.jar"
curl -fL -o "$${JMETER_HOME}/lib/cmdrunner-$${CMDRUNNER_VERSION}.jar" \
  "https://repo1.maven.org/maven2/kg/apc/cmdrunner/$${CMDRUNNER_VERSION}/cmdrunner-$${CMDRUNNER_VERSION}.jar"

echo "[user-data] Setting up PluginManagerCMD"
java -cp "$${JMETER_HOME}/lib/ext/jmeter-plugins-manager-$${PLUGINS_MANAGER_VERSION}.jar" \
  org.jmeterplugins.repository.PluginManagerCMDInstaller || true

echo "[user-data] Installing common JMeter plugins"
bash "$${JMETER_HOME}/bin/PluginsManagerCMD.sh" install jpgc-graphs-basic,jpgc-graphs-additional || true

echo "[user-data] Installing JWT dependency"
curl -fL -o "$${JMETER_HOME}/lib/java-jwt-4.5.0.jar" \
  "https://repo1.maven.org/maven2/com/auth0/java-jwt/4.5.0/java-jwt-4.5.0.jar"

# Provide a simple wrapper to run jmeter non-interactively
cat >/usr/local/bin/jmeter-run <<'WRAP'
#!/usr/bin/env bash
set -euo pipefail
if ! command -v jmeter >/dev/null 2>&1; then
  echo "jmeter not found in PATH" >&2
  exit 1
fi
jmeter "$@"
WRAP
chmod +x /usr/local/bin/jmeter-run

echo "[user-data] JMeter version:"
jmeter -v || true

echo "[user-data] Mark installation complete"
touch /opt/jmeter/.installed

# Optionally power off the instance so default state is Stopped
if [ "${var.jmeter_poweroff_after_setup}" = "true" ]; then
  echo "[user-data] Powering off instance"
  systemctl poweroff --no-wall || shutdown -h now || true
else
  echo "[user-data] Leaving instance running for SSM/interactive use"
fi
  EOT
}

resource "aws_instance" "jmeter" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.jmeter_instance_type
  subnet_id                   = local.jmeter_subnet_id
  vpc_security_group_ids      = [aws_security_group.jmeter_ec2_sg.id]
  iam_instance_profile        = local.jmeter_effective_instance_profile_name
  key_name                    = var.ssh_key_pair_name != "" ? var.ssh_key_pair_name : null
  associate_public_ip_address = false
  ebs_optimized               = true
  monitoring                  = true

  user_data                   = local.jmeter_user_data
  user_data_replace_on_change = true

  root_block_device {
    encrypted   = true
    volume_size = var.jmeter_volume_size
    volume_type = "gp3"
  }

  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  instance_initiated_shutdown_behavior = "stop"

  lifecycle {
    precondition {
      condition     = local.jmeter_effective_instance_profile_name != null
      error_message = "Provide jmeter_instance_profile_name or set allow_create_iam=true (with pipeline IAM perms) so the stack can create one."
    }
  }

  # Helpful explicit name; provider also applies default tags
  tags = {
    Name = local.jmeter_name
    Role = "jmeter"
  }
}

output "jmeter_instance_id" {
  description = "ID of the JMeter EC2 instance"
  value       = aws_instance.jmeter.id
}

output "jmeter_private_ip" {
  description = "Private IP of the JMeter EC2 instance"
  value       = aws_instance.jmeter.private_ip
}

output "jmeter_security_group_id" {
  description = "Security group ID for the JMeter instance"
  value       = aws_security_group.jmeter_ec2_sg.id
}
