module "sqs_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.sqs
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "sqs.amazonaws.com"
  description      = "Encryption key for SQS queues in ${var.environment} environment"
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
        AWS = [aws_iam_role.ec2_performance_role.arn]
      }
      Action = [
        "kms:Decrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      Resource = "*"
    },
    {
      Sid    = "AllowDMSSecretsAccess"
      Effect = "Allow"
      Principal = {
        AWS = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.project_prefix}-data-migration-dms-secrets-access"]
      }
      Action = [
        "kms:Decrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      Resource = "*"
    },
    {
      Sid    = "AllowLambdasSecretsAccess"
      Effect = "Allow"
      Principal = {
        AWS = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.project_prefix}-data-migration-dms-secrets-access*",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.project_prefix}-data-migration-reference-data-lambda*",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.project_prefix}-data-migration-dms-db-setup*",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.project_prefix}-data-migration-queue-populator-lambda*",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.project_prefix}-data-migration-processor-lambda*",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.project_prefix}-etl-ods-processor-lambda*",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.project_prefix}-etl-ods-consumer-lambda*",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.project_prefix}-ui-frontend-lambda*"
        ]
      }
      Action = [
        "kms:Decrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      Resource = "*"
    }
  ]
}
