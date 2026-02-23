module "aws_backup_destination" {
  source = "../../modules/aws-backup-destination"

  source_account_name = "${var.project}-shared"
  source_account_ids  = local.source_account_ids
  account_id          = var.mgmt_account_id
  region              = var.aws_region
  kms_key             = module.backup_destination_kms_key.arn

  enable_vault_protection       = var.backup_destination_enable_vault_protection
  vault_lock_type               = var.backup_destination_vault_lock_type
  vault_lock_min_retention_days = var.backup_destination_vault_lock_min_retention_days
  vault_lock_max_retention_days = var.backup_destination_vault_lock_max_retention_days
  changeable_for_days           = var.backup_destination_changeable_for_days
}
