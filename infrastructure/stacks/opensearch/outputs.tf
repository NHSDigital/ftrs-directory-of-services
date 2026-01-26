output "opensearch_collection_endpoint" {
  description = "The opensearch collection endpoint"
  value       = local.stack_enabled == 1 ? data.aws_opensearchserverless_collection.opensearch_serverless_collection[0].collection_endpoint : null
}

output "opensearch_dashboard_endpoint" {
  description = "The opensearch dashboard endpoint"
  value       = local.stack_enabled == 1 ? data.aws_opensearchserverless_collection.opensearch_serverless_collection[0].dashboard_endpoint : null
}
