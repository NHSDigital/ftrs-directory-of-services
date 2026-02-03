data "aws_kms_key" "secrets_manager_kms_key" {
  key_id = local.kms_aliases.secrets_manager
}

data "aws_kms_key" "ssm_kms_key" {
  key_id = local.kms_aliases.ssm
}

data "aws_kms_key" "s3_kms_key" {
  key_id = local.kms_aliases.s3
}
