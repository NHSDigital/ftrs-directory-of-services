locals {
  stack_enabled = var.opensearch_stack_enabled ? 1 : 0
  opensearch_collection_name = local.stack_enabled == 0 ? null : try(
    data.aws_opensearchserverless_collection.opensearch_serverless_collection[0].name,
    module.opensearch_serverless[0].name
  )
  opensearch_collection_endpoint = local.stack_enabled == 0 ? null : try(
    data.aws_opensearchserverless_collection.opensearch_serverless_collection[0].collection_endpoint,
    module.opensearch_serverless[0].endpoint
  )
}
