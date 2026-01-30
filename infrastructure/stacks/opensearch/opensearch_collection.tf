module "opensearch_serverless" {
  count = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0
  # Module version: 1.7.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-opensearch.git//modules/collection?ref=6f7113edebb53779de7225634f7e914bc6d59c8c"

  name             = "${local.project_prefix}${var.opensearch_collection_name}"
  description      = "OpenSearch Serverless collection for DynamoDB ingestion"
  type             = var.opensearch_type
  standby_replicas = var.opensearch_standby_replicas

  create_access_policy  = var.opensearch_create_access_policy
  create_network_policy = var.opensearch_create_network_policy
}
