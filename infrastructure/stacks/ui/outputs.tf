output "ui_cloudfront_distribution_url" {
  value       = local.stack_enabled == 1 ? module.ui_cloudfront[0].cloudfront_distribution_domain_name : null
  description = "The CloudFront distribution URL for the UI"
}

output "ui_cloudfront_distribution_id" {
  value       = local.stack_enabled == 1 ? module.ui_cloudfront[0].cloudfront_distribution_id : null
  description = "The CloudFront distribution ID for the UI"
}

output "cloudfront_5xx_health_check_id" {
  value       = local.stack_enabled == 1 ? aws_route53_health_check.cloudfront_5xx_errors[0].id : null
  description = "The ID of the Route53 health check monitoring CloudFront 5xx errors"
}

output "cloudfront_4xx_health_check_id" {
  value       = local.stack_enabled == 1 ? aws_route53_health_check.cloudfront_4xx_errors[0].id : null
  description = "The ID of the Route53 health check monitoring CloudFront 4xx errors"
}

output "cloudfront_latency_health_check_id" {
  value       = local.stack_enabled == 1 ? aws_route53_health_check.cloudfront_latency[0].id : null
  description = "The ID of the Route53 health check monitoring CloudFront latency"
}

output "calculated_health_check_id" {
  value       = local.stack_enabled == 1 ? aws_route53_health_check.calculated_health_check[0].id : null
  description = "The ID of the calculated health check monitoring CloudFront. This will be associated with Shield Advanced"
}

output "ui_session_store_table_name" {
  value       = local.stack_enabled == 1 ? "${local.resource_prefix}-session-store${local.workspace_suffix}" : null
  description = "The name of the DynamoDB session store table for the UI"
}
