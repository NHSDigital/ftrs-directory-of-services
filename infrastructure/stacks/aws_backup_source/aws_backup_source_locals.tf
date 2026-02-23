locals {
  stack_enabled = var.aws_backup_source_stack_enabled ? 1 : 0

  # Construct destination vault ARN directly to avoid cross-account provider dependency
  destination_vault_arn = "arn:aws:backup:${var.aws_region}:${var.mgmt_account_id}:backup-vault:${var.project}-shared-backup-vault"
  terraform_role_name   = "${var.repo_name}${var.environment != "mgmt" ? "-${var.environment}" : ""}-${var.account_github_runner_role_name}"
  terraform_role_arn    = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.terraform_role_name}"
  dynamodb_restore_testing_arns = [
    for table in values(local.dynamodb_tables) : table.arn
  ]

  backup_plan_config = {
    compliance_resource_types = ["RDS"]
    selection_tag             = var.backup_selection_tag
    rules = [
      {
        name     = "daily_kept_${var.backup_source_daily_retention_days}_days"
        schedule = var.backup_daily_schedule
        lifecycle = {
          delete_after = var.backup_source_daily_retention_days
        }
        copy_action = {
          delete_after = var.backup_destination_retention_days
        }
      },
      {
        name     = "weekly_kept_${var.backup_source_weekly_retention_days}_days"
        schedule = var.backup_weekly_schedule
        lifecycle = {
          delete_after = var.backup_source_weekly_retention_days
        }
        copy_action = {
          delete_after = var.backup_destination_retention_days
        }
      },
      {
        name     = "monthly_kept_${var.backup_source_monthly_retention_days}_days"
        schedule = var.backup_monthly_schedule
        lifecycle = {
          cold_storage_after = var.backup_source_monthly_cold_storage_after_days
          delete_after       = var.backup_source_monthly_retention_days
        }
        copy_action = {
          delete_after = var.backup_destination_retention_days
        }
      },
      {
        name                     = "point_in_time_recovery"
        schedule                 = var.backup_point_in_time_schedule
        enable_continuous_backup = true
        lifecycle = {
          delete_after = var.backup_source_pitr_retention_days
        }
        copy_action = {
          delete_after = var.backup_destination_retention_days
        }
      }
    ]
  }

  backup_plan_config_dynamodb = {
    enable                    = true
    selection_tag             = var.backup_selection_tag
    compliance_resource_types = ["DynamoDB"]
    rules = [
      {
        name     = "dynamodb_daily_kept_${var.backup_source_daily_retention_days}_days"
        schedule = var.backup_daily_schedule
        lifecycle = {
          delete_after = var.backup_source_daily_retention_days
        }
        copy_action = {
          delete_after = var.backup_destination_retention_days
        }
      },
      {
        name     = "dynamodb_weekly_kept_${var.backup_source_weekly_retention_days}_days"
        schedule = var.backup_weekly_schedule
        lifecycle = {
          delete_after = var.backup_source_weekly_retention_days
        }
        copy_action = {
          delete_after = var.backup_destination_retention_days
        }
      },
      {
        name     = "dynamodb_monthly_kept_${var.backup_source_monthly_retention_days}_days"
        schedule = var.backup_monthly_schedule
        lifecycle = {
          cold_storage_after = var.backup_source_monthly_cold_storage_after_days
          delete_after       = var.backup_source_monthly_retention_days
        }
        copy_action = {
          delete_after = var.backup_destination_retention_days
        }
      }
    ]
  }
}

module "aws_backup_source" {
  #checkov:skip=CKV_AWS_26: Revisit
  count = local.stack_enabled == 1 ? 1 : 0

  source = "../../modules/aws-backup-source"

  project_name     = var.project
  environment_name = var.environment
  aws_region       = var.aws_region
  resource_prefix  = local.resource_prefix

  backup_copy_vault_arn        = local.destination_vault_arn
  backup_copy_vault_account_id = var.mgmt_account_id

  # bootstrap_kms_key_arn = data.aws_kms_key.sns_kms_key.arn
  reports_bucket     = module.backup_reports_bucket.s3_bucket_id
  terraform_role_arn = local.terraform_role_arn

  backup_plan_config          = local.backup_plan_config
  backup_plan_config_dynamodb = local.backup_plan_config_dynamodb

  restore_testing_protected_resource_arns = local.dynamodb_restore_testing_arns
  restore_testing_enabled                 = var.restore_testing_enabled
}
