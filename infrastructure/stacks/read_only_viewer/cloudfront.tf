#trivy:ignore:AVD-AWS-0010
module "read_only_viewer_cloudfront" {
  # Module version: v5.0.1
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-cloudfront.git?ref=fc1010c0b53490d9b3911d2397726da80168f4fb"

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

  http_version                         = "http2and3"
  realtime_metrics_subscription_status = var.realtime_metrics_subscription_status
  create_monitoring_subscription       = var.create_monitoring_subscription

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
        http_port              = var.http_port
        https_port             = var.https_port
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
    cloudfront_default_certificate = false
    acm_certificate_arn            = data.aws_acm_certificate.domain_cert.arn
    ssl_support_method             = var.ssl_support_method
    minimum_protocol_version       = var.minimum_protocol_version
  }

  aliases = ["${var.stack_name}${local.workspace_suffix}.${local.env_domain_name}"]

  web_acl_id = data.aws_wafv2_web_acl.waf_web_acl.arn

  logging_config = {
    include_cookies = false
    bucket          = module.access_logging_bucket.s3_bucket_bucket_domain_name
    prefix          = var.access_logs_prefix
  }

  tags = {
    Name = "${local.resource_prefix}${local.workspace_suffix}"
  }
}
