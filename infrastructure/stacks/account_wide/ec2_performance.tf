// Performance EC2 instance(s) for performance testing in the account-wide stack.
// Creates a small Amazon Linux 2023 instance in a private subnet, reachable via SSM (Session Manager) only.
// Installs Apache JMeter on first boot and powers off the instance when installation completes (configurable).

locals {
  # Choose the first private subnet for Performance EC2. Safe because module.vpc is declared in this stack.
  performance_subnet_id = element(module.vpc.private_subnets, 0)
  # Name tag for Performance EC2 instance, scoped to this stack
  performance_name = "${var.project}-${var.environment}-${var.stack_name}-performance"
}

resource "aws_instance" "performance" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.performance_instance_type
  subnet_id                   = local.performance_subnet_id
  vpc_security_group_ids      = [aws_security_group.performance_ec2_sg.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2_performance_instance_profile.name
  associate_public_ip_address = false
  ebs_optimized               = true
  monitoring                  = true

  user_data = templatefile("${path.module}/templates/performance_user_data.sh.tmpl", {
    aws_region                         = var.aws_region,
    performance_version                = var.performance_version,
    performance_poweroff_after_setup   = var.performance_poweroff_after_setup,
    performance_jwt_dependency_version = var.performance_jwt_dependency_version
  })
  user_data_replace_on_change = true

  root_block_device {
    encrypted   = true
    volume_size = var.performance_volume_size
    volume_type = "gp3"
  }

  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  instance_initiated_shutdown_behavior = "stop"

  tags = {
    Name = local.performance_name
    Role = "performance"
  }

  depends_on = [
    aws_iam_role_policy_attachment.ec2_performance_ssm_core
  ]
}

# IAM role and instance profile for Performance EC2 (moved from account_policies)
resource "aws_iam_role" "ec2_performance_role" {
  name = "${var.project}-${var.environment}-ec2-performance"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_performance_ssm_core" {
  role       = aws_iam_role.ec2_performance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2_performance_instance_profile" {
  name = "${var.project}-${var.environment}-instance-profile-performance"
  role = aws_iam_role.ec2_performance_role.name
}

output "performance_instance_id" {
  description = "ID of the Performance EC2 instance"
  value       = aws_instance.performance.id
}

output "performance_private_ip" {
  description = "Private IP of the Performance EC2 instance"
  value       = aws_instance.performance.private_ip
}

output "performance_security_group_id" {
  description = "Security group ID for the Performance instance"
  value       = aws_security_group.performance_ec2_sg.id
}
