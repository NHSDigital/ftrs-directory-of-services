module "opensearch_serverless" {
  # Module version: 1.6.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-opensearch.git//modules/collection?ref=432e3866f1236f8a9b643e93b918a2c644cbeee7"

  name             = "${var.project}${var.opensearch_collection_name}"
  description      = "OpenSearch Serverless collection for DynamoDB ingestion"
  type             = var.opensearch_type
  standby_replicas = var.opensearch_standby_replicas

  create_access_policy  = var.opensearch_create_access_policy
  create_network_policy = var.opensearch_create_network_policy
}
