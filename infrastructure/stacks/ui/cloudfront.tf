#trivy:ignore:AVD-AWS-0010
module "ui_cloudfront" {
  # Module version: v5.0.1
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-cloudfront.git?ref=fc1010c0b53490d9b3911d2397726da80168f4fb"

  comment         = "CloudFront distribution for UI"
  price_class     = var.ui_cloudfront_price_class
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

  http_version                         = var.http_version
  realtime_metrics_subscription_status = var.realtime_metrics_subscription_status
  create_monitoring_subscription       = var.create_monitoring_subscription

  geo_restriction = {
    restriction_type = "whitelist"
    locations        = ["GB", "JE", "IM"]
  }

  origin = {
    s3_bucket = {
      domain_name           = module.ui_bucket.s3_bucket_bucket_regional_domain_name
      origin_access_control = "${local.resource_prefix}-s3-oac${local.workspace_suffix}"
    }

    lambda_function = {
      domain_name = replace(replace(aws_lambda_function_url.ui_lambda_url.function_url, "https://", ""), "/", "")
      custom_origin_config = {
        http_port              = var.http_port
        https_port             = var.https_port
        origin_protocol_policy = var.origin_protocol_policy
        origin_ssl_protocols   = var.origin_ssl_protocols
      }
    }
  }

  default_cache_behavior = {
    target_origin_id         = "lambda_function"
    allowed_methods          = ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"]
    cached_methods           = ["GET", "HEAD"]
    compress                 = true
    query_string             = true
    viewer_protocol_policy   = "redirect-to-https"
    origin_request_policy_id = aws_cloudfront_origin_request_policy.all_viewer_headers.id
    cache_policy_id          = data.aws_cloudfront_cache_policy.caching_disabled.id
  }

  ordered_cache_behavior = [
    {
      path_pattern           = "/_build/*"
      target_origin_id       = "s3_bucket"
      allowed_methods        = ["GET", "HEAD"]
      cached_methods         = ["GET", "HEAD"]
      compress               = true
      query_string           = true
      viewer_protocol_policy = "redirect-to-https"
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
      path_pattern           = "/images/*"
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

data "aws_cloudfront_cache_policy" "caching_disabled" {
  name = "Managed-CachingDisabled"
}

resource "aws_cloudfront_origin_request_policy" "all_viewer_headers" {
  name = "${local.resource_prefix}-all-viewer-headers"

  headers_config {
    header_behavior = "allViewer"
  }

  cookies_config {
    cookie_behavior = "all"
  }

  query_strings_config {
    query_string_behavior = "all"
  }
}
