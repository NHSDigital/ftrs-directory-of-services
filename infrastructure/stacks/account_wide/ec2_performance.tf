// Performance EC2 instance(s) for performance testing in the account-wide stack.
// Creates a small Amazon Linux 2023 instance in a private subnet, reachable via SSM (Session Manager) only.
// Installs Apache JMeter on first boot and powers off the instance when installation completes (configurable).

locals {
  # Choose the first private subnet for Performance EC2. Safe because module.vpc is declared in this stack.
  performance_subnet_id = element(module.vpc.private_subnets, 0)
  # Name tag for Performance EC2 instance, scoped to this stack
  performance_name = "${local.account_prefix}-performance"

  # ARN prefix locals to avoid gitleaks arns3 false positives
  s3_arn_prefix = "arn:aws:s3"

  # Performance S3 bucket names (account prefix + provided suffix variables)
  performance_parameter_files_bucket_name = "${local.account_prefix}-${var.performance_parameter_files_bucket_name}"
  performance_artifacts_bucket_name       = "${local.account_prefix}-${var.performance_artifacts_bucket_name}"

  # S3 bucket and object ARNs for IAM policy (composed using prefix to avoid inline arn literal)
  performance_parameter_files_bucket_arn  = "${local.s3_arn_prefix}:::${local.performance_parameter_files_bucket_name}"
  performance_artifacts_bucket_arn        = "${local.s3_arn_prefix}:::${local.performance_artifacts_bucket_name}"
  performance_parameter_files_objects_arn = "${local.s3_arn_prefix}:::${local.performance_parameter_files_bucket_name}/*"
  performance_artifacts_objects_arn       = "${local.s3_arn_prefix}:::${local.performance_artifacts_bucket_name}/*"

  # Performance Secrets: prefix, paths, and full ARNs for IAM policy
  performance_secret_prefix                  = "/${local.repo_env_path}/"
  performance_secret_api_jmeter_pks_key_path = "${local.performance_secret_prefix}${var.performance_secret_api_jmeter_pks_key_name}*"
  performance_secret_api_ca_cert_path        = "${local.performance_secret_prefix}${var.performance_secret_api_ca_cert_name}*"
  performance_secret_api_ca_pk_path          = "${local.performance_secret_prefix}${var.performance_secret_api_ca_pk_name}*"

  performance_secret_api_jmeter_pks_key_arn = "arn:aws:secretsmanager:${var.aws_region}:${local.account_id}:secret:${local.performance_secret_api_jmeter_pks_key_path}"
  performance_secret_api_ca_cert_arn        = "arn:aws:secretsmanager:${var.aws_region}:${local.account_id}:secret:${local.performance_secret_api_ca_cert_path}"
  performance_secret_api_ca_pk_arn          = "arn:aws:secretsmanager:${var.aws_region}:${local.account_id}:secret:${local.performance_secret_api_ca_pk_path}"
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
  name = "${local.account_prefix}-ec2-performance"
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
  name = "${local.account_prefix}-instance-profile-performance"
  role = aws_iam_role.ec2_performance_role.name
}

# S3 access required for Performance EC2 (explicit performance buckets only)
# Includes bucket-level metadata and object-level CRUD plus multipart support
data "aws_iam_policy_document" "ec2_performance_s3" {
  # Bucket-level metadata actions on explicit Performance buckets
  statement {
    sid = "AllowS3BucketMetadataForPerformance"
    actions = [
      "s3:ListBucket",
      "s3:GetBucketLocation",
      "s3:ListBucketMultipartUploads"
    ]
    resources = [
      # Explicit Performance testing buckets (parameter files + artifacts)
      local.performance_parameter_files_bucket_arn,
      local.performance_artifacts_bucket_arn
    ]
  }

  # Object-level CRUD and multipart actions on explicit Performance buckets
  statement {
    sid = "AllowS3ObjectAccessForPerformance"
    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:CreateMultipartUpload",
      "s3:UploadPart",
      "s3:ListMultipartUploadParts",
      "s3:CompleteMultipartUpload",
      "s3:AbortMultipartUpload"
    ]
    resources = [
      # Objects within the Performance parameter files and artifacts buckets only
      local.performance_parameter_files_objects_arn,
      local.performance_artifacts_objects_arn
    ]
  }
}

resource "aws_iam_role_policy" "ec2_performance_s3" {
  name   = "${local.account_prefix}-ec2-performance-s3"
  role   = aws_iam_role.ec2_performance_role.id
  policy = data.aws_iam_policy_document.ec2_performance_s3.json
}

# Secrets Manager read access restricted to three explicit secrets used by performance tests
data "aws_iam_policy_document" "ec2_performance_secrets" {
  statement {
    sid = "AllowGetExplicitPerformanceSecrets"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [
      # Explicit secrets required by Performance EC2
      local.performance_secret_api_jmeter_pks_key_arn,
      local.performance_secret_api_ca_cert_arn,
      local.performance_secret_api_ca_pk_arn
    ]
  }
}

resource "aws_iam_role_policy" "ec2_performance_secrets" {
  name   = "${local.account_prefix}-ec2-performance-secrets"
  role   = aws_iam_role.ec2_performance_role.id
  policy = data.aws_iam_policy_document.ec2_performance_secrets.json
}

# KMS access limited to AWS-managed keys for S3 and Secrets Manager only (alias/aws/s3, alias/aws/secretsmanager)
# Enforced via kms:ViaService + kms:ResourceAliases conditions
data "aws_iam_policy_document" "ec2_performance_kms" {
  statement {
    sid = "AllowKmsUseForS3AndSecrets"
    actions = [
      "kms:Decrypt",
      "kms:Encrypt",
      "kms:GenerateDataKey",
      "kms:DescribeKey"
    ]
    # Use all resources, then constrain to AWS-managed aliases via condition below
    resources = ["*"]

    # Allow usage only when invoked via these AWS services (prevents direct KMS API use)
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values = [
        "s3.${var.aws_region}.amazonaws.com",
        "secretsmanager.${var.aws_region}.amazonaws.com"
      ]
    }

    # Restrict to AWS-managed KMS keys behind these aliases
    condition {
      test     = "ForAnyValue:StringEquals"
      variable = "kms:ResourceAliases"
      values = [
        "alias/aws/s3",
        "alias/aws/secretsmanager"
      ]
    }
  }
}

resource "aws_iam_role_policy" "ec2_performance_kms" {
  name   = "${local.account_prefix}-ec2-performance-kms"
  role   = aws_iam_role.ec2_performance_role.id
  policy = data.aws_iam_policy_document.ec2_performance_kms.json
}
