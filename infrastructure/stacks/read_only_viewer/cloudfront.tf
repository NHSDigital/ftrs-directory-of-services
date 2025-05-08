module "read_only_viewer_cloudfront" {
  source  = "terraform-aws-modules/cloudfront/aws"
  version = "4.1.0"

  comment         = "CloudFront distribution for read-only viewer"
  price_class     = "PriceClass_100"
  is_ipv6_enabled = true


  create_origin_access_control = true
  origin_access_control = {
    s3_oac = {
      description      = "CloudFront access to S3"
      origin_type      = "s3"
      signing_behavior = "always"
      signing_protocol = "sigv4"
    }
  }

  origin = {
    s3_bucket = {
      domain_name           = module.read_only_viewer_bucket.s3_bucket_bucket_regional_domain_name
      origin_access_control = "s3_oac"
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
}
