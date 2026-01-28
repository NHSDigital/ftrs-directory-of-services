output "opensearch_collection_endpoint" {
  description = "The opensearch collection endpoint"
  value       = local.stack_enabled == 1 && length(module.opensearch_serverless) > 0 ? try(module.opensearch_serverless[0].endpoint, null) : null
}

output "opensearch_dashboard_endpoint" {
  description = "The opensearch dashboard endpoint"
  value       = local.stack_enabled == 1 && length(module.opensearch_serverless) > 0 ? try(module.opensearch_serverless[0].dashboard_endpoint, null) : null
}
