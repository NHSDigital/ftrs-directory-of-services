output "opensearch_collection_endpoint" {
  description = "The opensearch collection endpoint"
  value       = data.aws_opensearchserverless_collection.opensearch_serverless_collection.collection_endpoint
}

output "opensearch_dashboard_endpoint" {
  description = "The opensearch dashboard endpoint"
  value       = data.aws_opensearchserverless_collection.opensearch_serverless_collection.dashboard_endpoint
}
