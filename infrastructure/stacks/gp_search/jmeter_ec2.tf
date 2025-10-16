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
# tfsec:ignore:aws-vpc-no-public-egress-sgr -- JMeter host requires outbound 80/443 to the internet for package and plugin downloads and to reach external test endpoints. Restricting to specific CIDRs is not feasible; traffic still routes via private subnets/NAT or VPC endpoints where present.
resource "aws_vpc_security_group_egress_rule" "egress_https" {
  security_group_id = aws_security_group.jmeter_ec2_sg.id
  description       = "Allow HTTPS egress"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}

# tfsec:ignore:aws-vpc-no-public-egress-sgr -- See justification above for HTTPS; HTTP is used for some mirrors/tools. Prefer HTTPS where possible.
resource "aws_vpc_security_group_egress_rule" "egress_http" {
  security_group_id = aws_security_group.jmeter_ec2_sg.id
  description       = "Allow HTTP egress"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}

# IAM role to allow SSM (optional but useful)
resource "aws_iam_role" "jmeter_ec2_role" {
  name = "${local.jmeter_name}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.jmeter_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "jmeter_ec2_profile" {
  name = "${local.jmeter_name}-instance-profile"
  role = aws_iam_role.jmeter_ec2_role.name
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

    echo "[user-data] Updating packages"
    dnf -y update || true

    echo "[user-data] Installing Java 17 (Amazon Corretto) and utilities"
    dnf -y install java-17-amazon-corretto-headless unzip jq curl wget tar || true

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

    # Power off the instance so default state is Stopped
    echo "[user-data] Powering off instance"
    systemctl poweroff --no-wall || shutdown -h now || true
  EOT
}

resource "aws_instance" "jmeter" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.jmeter_instance_type
  subnet_id                   = local.jmeter_subnet_id
  vpc_security_group_ids      = [aws_security_group.jmeter_ec2_sg.id]
  iam_instance_profile        = aws_iam_instance_profile.jmeter_ec2_profile.name
  key_name                    = var.ssh_key_pair_name != "" ? var.ssh_key_pair_name : null
  associate_public_ip_address = false
  ebs_optimized               = true
  monitoring                  = true

  user_data = local.jmeter_user_data

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
