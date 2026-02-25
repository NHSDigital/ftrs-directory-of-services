module "aws_backup_source" {
  count  = local.stack_enabled
  source = "../../modules/aws-backup-source"

  project_name     = var.project
  environment_name = var.environment
  aws_region       = var.aws_region
  resource_prefix  = local.resource_prefix

  backup_copy_vault_arn        = local.destination_vault_arn
  backup_copy_vault_account_id = var.mgmt_account_id

  bootstrap_kms_key_arn = module.backup_sns_kms_key[0].arn
  reports_bucket        = module.backup_reports_bucket[0].s3_bucket_id
  terraform_role_arn    = local.terraform_role_arn

  backup_plan_config          = local.backup_plan_config
  backup_plan_config_dynamodb = local.backup_plan_config_dynamodb

  restore_testing_enabled = var.restore_testing_enabled
}
