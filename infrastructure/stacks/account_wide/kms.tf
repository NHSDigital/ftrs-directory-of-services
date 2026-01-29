module "sqs_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.sqs
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "sqs.amazonaws.com"
  description      = "Encryption key for SQS queues in ${var.environment} environment"

  additional_policy_statements = [
    {
      Sid    = "AllowCloudWatchAlarmsAccess"
      Effect = "Allow"
      Principal = {
        Service = "cloudwatch.amazonaws.com"
      }
      Action = [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ]
      Resource = "*"
    },
    {
      Sid    = "AllowSNSAccess"
      Effect = "Allow"
      Principal = {
        Service = "sns.amazonaws.com"
      }
      Action = [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ]
      Resource = "*"
    }
  ]
}

module "secrets_manager_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.secrets_manager
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "secretsmanager.amazonaws.com"
  description      = "Encryption key for Secrets Manager in ${var.environment} environment"

  additional_policy_statements = [
    {
      Sid    = "AllowEC2SecretsAccess"
      Effect = "Allow"
      Principal = {
        AWS = [
          aws_iam_role.ec2_performance_role.arn
        ]
      }
      Action = [
        "kms:Decrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      Resource = "*"
    },
    {
      Sid    = "AllowGitHubRunnerAccess"
      Effect = "Allow"
      Principal = {
        AWS = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.account_prefix}-${var.app_github_runner_role_name}",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.account_prefix}-${var.account_github_runner_role_name}"
        ]
      }
      Action = [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      Resource = "*"
    }
  ]
}

module "opensearch_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.opensearch
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "opensearchservice.amazonaws.com"
  description      = "Encryption key for OpenSearch in ${var.environment} environment"
}

module "rds_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.rds
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "rds.amazonaws.com"
  description      = "Encryption key for RDS instances in ${var.environment} environment"
}

module "dynamodb_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.dynamodb
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "dynamodb.amazonaws.com"
  description      = "Encryption key for DynamoDB tables in ${var.environment} environment"
}

module "dms_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.dms
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "dms.amazonaws.com"
  description      = "Encryption key for DMS in ${var.environment} environment"
}

module "ssm_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.ssm
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "ssm.amazonaws.com"
  description      = "Encryption key for SSM parameters in ${var.environment} environment"

  additional_policy_statements = [
    {
      Sid    = "AllowGitHubRunnerAccess"
      Effect = "Allow"
      Principal = {
        AWS = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.account_prefix}-${var.app_github_runner_role_name}",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.account_prefix}-${var.account_github_runner_role_name}"
        ]
      }
      Action = [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      Resource = "*"
    }
  ]
}

module "s3_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.s3
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "s3.amazonaws.com"
  description      = "Encryption key for S3 buckets in ${var.environment} environment"
}
