module "read_only_viewer_cloudfront" {
  # Module version: v4.1.0
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-cloudfront.git?ref=d66669f42ec922cb4b1acea8e4a17e5f6c6c9a15"

  comment         = "CloudFront distribution for read-only viewer"
  price_class     = var.read_only_viewer_cloudfront_price_class
  is_ipv6_enabled = true


  create_origin_access_control = true
  origin_access_control = {
    "${local.resource_prefix}-s3-oac${local.workspace_suffix}" = {
      description      = "CloudFront access to S3"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  http_version = "http2and3"

  geo_restriction = {
    restriction_type = "whitelist"
    locations        = ["GB", "JE", "IM"]
  }

  origin = {
    s3_bucket = {
      domain_name           = module.read_only_viewer_bucket.s3_bucket_bucket_regional_domain_name
      origin_access_control = "${local.resource_prefix}-s3-oac${local.workspace_suffix}"
    }

    lambda_function = {
      domain_name = replace(replace(aws_lambda_function_url.frontend_lambda_url.function_url, "https://", ""), "/", "")
      custom_origin_config = {
        http_port              = 80
        https_port             = 443
        origin_protocol_policy = "https-only"
        origin_ssl_protocols   = ["TLSv1.2"]
      }
    }
  }

  default_cache_behavior = {
    target_origin_id       = "lambda_function"
    allowed_methods        = ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    query_string           = true
    viewer_protocol_policy = "redirect-to-https"
  }

  ordered_cache_behavior = [
    {
      path_pattern           = "/_build/*"
      target_origin_id       = "s3_bucket"
      viewer_protocol_policy = "redirect-to-https"
      allowed_methods        = ["GET", "HEAD"]
      cached_methods         = ["GET", "HEAD"]
      compress               = true
      query_string           = true
    },
    {
      path_pattern           = "/assets/*"
      target_origin_id       = "s3_bucket"
      allowed_methods        = ["GET", "HEAD"]
      cached_methods         = ["GET", "HEAD"]
      compress               = true
      query_string           = true
      viewer_protocol_policy = "redirect-to-https"
    },
    {
      path_pattern           = "favicon.ico"
      target_origin_id       = "s3_bucket"
      allowed_methods        = ["GET", "HEAD"]
      cached_methods         = ["GET", "HEAD"]
      compress               = true
      query_string           = true
      viewer_protocol_policy = "redirect-to-https"
    }
  ]

  viewer_certificate = {
    cloudfront_default_certificate = true
  }

  web_acl_id = aws_wafv2_web_acl.read_only_viewer_waf_web_acl.arn
  logging_config = {
    include_cookies = false
    bucket          = module.access_logging_bucket.s3_bucket_bucket_domain_name
    prefix          = var.access_logs_prefix
  }
}
