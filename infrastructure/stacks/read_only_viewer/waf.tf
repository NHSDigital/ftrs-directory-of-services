resource "aws_wafv2_web_acl" "read_only_viewer_waf_web_acl" {
  name        = "${local.resource_prefix}-${var.read_only_viewer_waf_name}${local.workspace_suffix}"
  description = "WAF Web ACL for read only viewer"
  scope       = var.read_only_viewer_waf_scope

  default_action {
    allow {}
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesAmazonIpReputationList"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAmazonIpReputationList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesAmazonIpReputationList"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesAnonymousIpList"
    priority = 4

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAnonymousIpList"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesAnonymousIpList"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesAdminProtectionRuleSet"
    priority = 5

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAdminProtectionRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesAdminProtectionRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "rate-limit-rule"
    priority = 6

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit                 = 100
        aggregate_key_type    = "FORWARDED_IP"
        evaluation_window_sec = 120
        forwarded_ip_config {
          fallback_behavior = "NO_MATCH"
          header_name       = "X-Forwarded-For"
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "rate-limit-rule"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "allowed-countries-rule"
    priority = 7
    action {
      block {}
    }
    statement {
      not_statement {
        statement {
          geo_match_statement {
            country_codes = ["GB", "JE", "IM"]
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "allowed-countries-rule"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "friendly-metric-name"
    sampled_requests_enabled   = true
  }

  provider = aws.us-east-1
}

resource "aws_wafv2_web_acl_logging_configuration" "read_only_viewer_waf_logging_configuration" {
  log_destination_configs = [aws_cloudwatch_log_group.read_only_viewer_waf_log_group.arn]
  resource_arn            = aws_wafv2_web_acl.read_only_viewer_waf_web_acl.arn
  provider                = aws.us-east-1
}
