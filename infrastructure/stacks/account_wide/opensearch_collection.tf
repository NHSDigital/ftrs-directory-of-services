module "opensearch_serverless" {
  source  = "terraform-aws-modules/opensearch/aws//modules/collection"
  version = "1.6.0"

  name             = "${var.project}${var.opensearch_collection_name}"
  description      = "OpenSearch Serverless collection for DynamoDB ingestion"
  type             = var.opensearch_type
  standby_replicas = var.opensearch_standby_replicas

  create_access_policy  = var.opensearch_create_access_policy
  create_network_policy = var.opensearch_create_network_policy
}
