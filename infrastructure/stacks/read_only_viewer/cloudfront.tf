module "read_only_viewer_cloudfront" {
  source                         = "../../modules/cloudfront"
  s3_bucket_regional_domain_name = module.read_only_viewer_bucket.s3_bucket_bucket_regional_domain_name
  cloud_front_name               = "${local.resource_prefix}-${var.read_only_viewer_cloud_front_name}${local.workspace_suffix}"
  s3_bucket_id                   = module.read_only_viewer_bucket.s3_bucket_id
  comment                        = "CloudFront distribution for read-only viewer bucket"
  web_acl_id                     = aws_wafv2_web_acl.read_only_viewer_waf_web_acl.arn
}
