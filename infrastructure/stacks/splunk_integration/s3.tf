module "firehose_backup_s3" {
  count                 = local.is_primary_environment ? 1 : 0
  source                = "../../modules/s3"
  bucket_name           = "${var.project}-${var.environment}-${var.firehose_name}-backup"
  s3_encryption_key_arn = data.aws_kms_key.s3_kms_key.arn
  enable_kms_encryption = var.enable_firehose_s3_kms_encryption
}
