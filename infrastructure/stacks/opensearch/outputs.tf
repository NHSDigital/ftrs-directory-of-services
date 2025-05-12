output "opensearch_collection_endpoint" {
  description = "The opensearch collection endpoint"
  value       = module.opensearch_serverless.endpoint
}

output "opensearch_dashboard_endpoint" {
  description = "The opensearch dashboard endpoint"
  value       = module.opensearch_serverless.dashboard_endpoint
}
