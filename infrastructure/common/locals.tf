locals {
  account_id        = data.aws_caller_identity.current.id
  workspace_suffix  = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  artefacts_bucket  = "${var.repo_name}-mgmt-${var.artefacts_bucket_name}"
  project_prefix    = "${var.project}-${var.environment}"
  resource_prefix   = "${local.project_prefix}-${var.stack_name}"
  account_prefix    = "${var.repo_name}-${var.environment}"
  root_domain_name  = "${var.environment}.${var.root_domain_name}"
  s3_logging_bucket = "${local.account_prefix}-${var.s3_logging_bucket_name}"

  artefact_base_path = var.release_tag != "" ? "releases/${var.release_tag}" : "${terraform.workspace}/${var.commit_hash}"

  # Deploy certain resources (e.g., databases, backup SSM) only in default Terraform workspace.
  is_primary_environment = terraform.workspace == "default"

  dynamodb_tables = {
    for table_name in var.dynamodb_table_names :
    table_name => {
      arn = "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/${local.project_prefix}-database-${table_name}${local.workspace_suffix}"
    }
  }

  organisation_table_arn = "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/${local.project_prefix}-database-${var.organisation_table_name}"

  domain_cross_account_role = "${var.repo_name}-mgmt-domain-name-cross-account-access"

  env_domain_name = "${var.environment}.${var.root_domain_name}"

  s3_trust_store_bucket_name = "${local.account_prefix}-${var.s3_trust_store_bucket_name}"

  trust_store_file_path = "${var.environment}/truststore.pem"

  env_sso_roles = [
    for role in var.sso_roles : "arn:aws:iam::${local.account_id}:role/aws-reserved/sso.amazonaws.com/${var.aws_region}/${role}"
  ]

  kms_aliases = {
    sqs             = "alias/${local.project_prefix}-sqs-kms"
    secrets_manager = "alias/${local.project_prefix}-secrets-manager-kms"
    ssm             = "alias/${local.project_prefix}-ssm-kms"
    dms             = "alias/${local.project_prefix}-dms-kms"
    dynamodb        = "alias/${local.project_prefix}-dynamodb-kms"
    s3              = "alias/${local.project_prefix}-s3-kms"
    rds             = "alias/${local.project_prefix}-rds-kms"
    opensearch      = "alias/${local.project_prefix}-opensearch-kms"
  }

  opensearch_collection_name = var.opensearch_collection_name
  opensearch_index_name      = "${var.index_base}${local.workspace_suffix}"
}
