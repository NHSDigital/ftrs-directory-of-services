module "sqs_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.sqs
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "sqs.amazonaws.com"
  description      = "Encryption key for SQS queues in ${var.environment} environment"
}

module "sns_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.sns
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "sns.amazonaws.com"
  description      = "Encryption key for SNS topics in ${var.environment} environment"

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
      Resource  = "*"
      Condition = {}
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
      Resource  = "*"
      Condition = {}
    },
    {
      Sid    = "AllowAthenaConnectorSecretsAccess"
      Effect = "Allow"
      Principal = {
        AWS = ["*"]
      }
      Action = [
        "kms:Decrypt",
        "kms:DescribeKey"
      ]
      Resource = "*"
      Condition = {
        ArnLike = {
          "aws:PrincipalArn" = [
            "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/serverlessrepo-${local.project_prefix}-*"
          ]
        }
      }
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

  additional_policy_statements = [
    {
      Sid    = "AllowRDSEnhancedAccess"
      Effect = "Allow"
      Principal = {
        Service = ["rds.amazonaws.com"]
      }
      Action = [
        "kms:CreateGrant",
        "kms:ListGrants",
        "kms:RevokeGrant"
      ]
      Resource = "*"
      Condition = {
        StringEquals = {
          "kms:ViaService" = ["rds.${var.aws_region}.amazonaws.com"]
        }
      }
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
      Resource  = "*"
      Condition = {}
    }
  ]
}

module "dynamodb_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.dynamodb
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "dynamodb.amazonaws.com"
  description      = "Encryption key for DynamoDB tables in ${var.environment} environment"

  additional_policy_statements = [
    {
      Sid    = "AllowDynamoDBEnhancedAccess"
      Effect = "Allow"
      Principal = {
        Service = ["dynamodb.amazonaws.com"]
      }
      Action = [
        "kms:CreateGrant",
        "kms:ListGrants",
        "kms:RevokeGrant"
      ]
      Resource = "*"
      Condition = {
        StringEquals = {
          "kms:ViaService" = ["dynamodb.${var.aws_region}.amazonaws.com"]
        }
      }
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
        "kms:DescribeKey",
        "kms:CreateGrant",
        "kms:RetireGrant"
      ]
      Resource  = "*"
      Condition = {}
    }
  ]
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

  additional_policy_statements = [
    {
      "Sid" : "AllowS3UseOfKeyForTruststore",
      "Effect" : "Allow",
      "Principal" : {
        "Service" : "s3.amazonaws.com"
      },
      "Action" : [
        "kms:Decrypt",
        "kms:DescribeKey"
      ],
      "Resource" : "*",
      "Condition" : {
        "StringEquals" : {
          "aws:SourceAccount" : "${local.account_id}",
          "kms:ViaService" : "s3.${var.aws_region}.amazonaws.com"
        }
      }
    }
  ]
}

module "firehose_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.firehose
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "firehose.amazonaws.com"
  description      = "Encryption key for Firehose in ${var.environment} environment"
}

module "scheduler_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.scheduler
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "scheduler.amazonaws.com"
  description      = "Encryption key for EventBridge scheduler in ${var.environment} environment"
  additional_policy_statements = [
    {
      Sid    = "AllowEventBridgeSchedulerToUseKMS"
      Effect = "Allow"
      Principal = {
        Service = ["scheduler.amazonaws.com"]
      }
      Action = [
        "kms:CreateGrant",
        "kms:RetireGrant",
        "kms:Decrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      Resource = "*"
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
      }
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
      Resource  = "*"
      Condition = {}
    }
  ]
}

module "lambda_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.lambda
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "lambda.amazonaws.com"
  description      = "Encryption key for Lambda environment variables in ${var.environment} environment"

  additional_policy_statements = [
    {
      Sid    = "AllowLambdaExecutionRoleAccess"
      Effect = "Allow"
      Principal = {
        AWS = [aws_iam_role.splunk_hec_transformer_role.arn]
      }
      Action = [
        "kms:Decrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      Resource  = "*"
      Condition = {}
    }
  ]
}

module "cloudtrail_encryption_key" {
  source           = "../../modules/kms"
  alias_name       = local.kms_aliases.cloudtrail
  account_id       = data.aws_caller_identity.current.account_id
  aws_service_name = "cloudtrail.amazonaws.com"
  description      = "Encryption key for CloudTrail in ${var.environment} environment"
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
      Resource  = "*"
      Condition = {}
    }
  ]
}
