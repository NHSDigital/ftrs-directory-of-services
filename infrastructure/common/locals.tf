locals {
  account_id        = data.aws_caller_identity.current.id
  workspace_suffix  = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  artefacts_bucket  = "${var.repo_name}-mgmt-${var.artefacts_bucket_name}"
  resource_prefix   = "${var.project}-${var.environment}-${var.stack_name}"
  account_prefix    = "${var.repo_name}-${var.environment}"
  root_domain_name  = "${var.environment}.${var.root_domain_name}"
  s3_logging_bucket = "${local.account_prefix}-${var.s3_logging_bucket_name}"

  # Deploy certain resources (e.g., databases, backup SSM) only in default Terraform workspace.
  is_primary_environment = terraform.workspace == "default"
  rds_environments       = var.environment == "dev" || var.environment == "test" || var.environment == "int"

  dynamodb_tables = {
    for table_name in var.dynamodb_table_names :
    table_name => {
      arn = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.project}-${var.environment}-database-${table_name}${local.workspace_suffix}"
    }
  }

  dos_search_organisation_table_arn = "arn:aws:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.project}-${var.environment}-database-${var.dos_search_organisation_table_name}"

  domain_cross_account_role = "${var.repo_name}-mgmt-domain-name-cross-account-access"

  env_domain_name = "${var.environment}.${var.root_domain_name}"

  s3_trust_store_bucket_name = "${local.account_prefix}-${var.s3_trust_store_bucket_name}"

  trust_store_file_path = "${var.environment}/truststore.pem"

  env_sso_roles = [
    for role in var.sso_roles : "arn:aws:iam::${local.account_id}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/${role}"
  ]
}
