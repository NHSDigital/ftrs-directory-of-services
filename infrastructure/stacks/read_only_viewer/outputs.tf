output "read_only_viewer_cloudfront_distribution_url" {
  value       = module.read_only_viewer_cloudfront.cloudfront_distribution_domain_name
  description = "The CloudFront distribution URL for the read-only viewer"
}

output "read_only_viewer_cloudfront_distribution_id" {
  value       = module.read_only_viewer_cloudfront.cloudfront_distribution_id
  description = "The CloudFront distribution ID for the read-only viewer"
}

output "cloudfront_5xx_health_check_id" {
  value       = aws_route53_health_check.cloudfront_5xx_errors.id
  description = "The ID of the Route53 health check monitoring CloudFront 5xx errors"
}

output "cloudfront_4xx_health_check_id" {
  value       = aws_route53_health_check.cloudfront_4xx_errors.id
  description = "The ID of the Route53 health check monitoring CloudFront 4xx errors"
}

output "cloudfront_latency_health_check_id" {
  value       = aws_route53_health_check.cloudfront_latency.id
  description = "The ID of the Route53 health check monitoring CloudFront latency"
}
