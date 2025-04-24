output "read_only_viewer_cloudfront_distribution_url" {
  value       = module.read_only_viewer_clodufront.cloudfront_distribution_domain_name
  description = "The CloudFront distribution URL for the read-only viewer."
}
