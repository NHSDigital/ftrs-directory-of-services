resource "aws_wafv2_web_acl" "waf_web_acl" {
  name        = "${local.resource_prefix}-${var.waf_name}"
  description = "WAF Web ACL"
  scope       = var.waf_scope

  default_action {
    allow {}
  }

  rule {
    name     = "allowed-countries-rule"
    priority = 11
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

  rule {
    name     = "AWSManagedRulesAmazonIpReputationList"
    priority = 21

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
    priority = 31

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
    name     = "rate-limit-rule"
    priority = 41

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
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 51

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
    priority = 61

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
    name     = "AWSManagedRulesAdminProtectionRuleSet"
    priority = 71

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
    name     = "AWSManagedRulesBotControlRuleSet"
    priority = 81

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesBotControlRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesBotControlRuleSet"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${local.resource_prefix}-metric"
    sampled_requests_enabled   = true
  }

  provider = aws.us-east-1
}

resource "aws_wafv2_web_acl_logging_configuration" "waf_logging_configuration" {
  log_destination_configs = [aws_cloudwatch_log_group.waf_log_group.arn]
  resource_arn            = aws_wafv2_web_acl.waf_web_acl.arn
  provider                = aws.us-east-1
}

# Regional Web ACL summary:
# - AWS Managed rule groups block (AmazonIpReputation, KnownBadInputs, BotControl, Common, Linux, Unix).
# - BotControl managed rule group rules count (SignalNonBrowserUserAgent, CategoryHttpLibrary).
# - BotControl and Common exclude APIM/Apigee allowlist via scope-down when CIDRs are provided.

# Regional Web ACL
resource "aws_wafv2_web_acl" "regional_waf_web_acl" {
  name        = "${local.resource_prefix}-${var.regional_waf_name}"
  description = "Regional WAF Web ACL"
  scope       = var.regional_waf_scope

  default_action {
    allow {}
  }

  # Managed rule groups
  rule {
    name     = "AWSManagedRulesAmazonIpReputationList"
    priority = 0

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
      cloudwatch_metrics_enabled = false
      metric_name                = "${local.resource_prefix}-regional-waf-aws-managed-ip-reputation-list"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesBotControlRuleSet"
    priority = 10

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesBotControlRuleSet"
        vendor_name = "AWS"

        rule_action_override {
          name = "CategoryHttpLibrary"
          action_to_use {
            count {}
          }
        }

        rule_action_override {
          name = "SignalNonBrowserUserAgent"
          action_to_use {
            count {}
          }
        }

        # Exclude APIGEE host IPs from BotControl evaluation.
        dynamic "scope_down_statement" {
          for_each = length(local.apim_apigee_cidrs_normalized) > 0 ? [1] : []
          content {
            not_statement {
              statement {
                ip_set_reference_statement {
                  arn = aws_wafv2_ip_set.apim_apigee_allowlist_regional[0].arn
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "${local.resource_prefix}-regional-waf-aws-managed-bot-control"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 20

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
      cloudwatch_metrics_enabled = false
      metric_name                = "${local.resource_prefix}-regional-waf-aws-managed-known-bad-inputs"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 30

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"

        # Exclude APIGEE host IPs from Common Rule Set evaluation.
        dynamic "scope_down_statement" {
          for_each = length(local.apim_apigee_cidrs_normalized) > 0 ? [1] : []
          content {
            not_statement {
              statement {
                ip_set_reference_statement {
                  arn = aws_wafv2_ip_set.apim_apigee_allowlist_regional[0].arn
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "${local.resource_prefix}-regional-waf-aws-managed-common-rules"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesLinuxRuleSet"
    priority = 40

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesLinuxRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "${local.resource_prefix}-regional-waf-aws-managed-linux-rules"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesUnixRuleSet"
    priority = 50

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesUnixRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "${local.resource_prefix}-regional-waf-aws-managed-unix-rules"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = false
    metric_name                = "${local.resource_prefix}-regional-waf"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_ip_set" "apim_apigee_allowlist_regional" {
  count              = length(local.apim_apigee_cidrs_normalized) > 0 ? 1 : 0
  name               = "${local.resource_prefix}-apim-apigee-allowlist-regional"
  description        = "IP set for APIM Apigee allowlist regional scope"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"

  addresses = local.apim_apigee_cidrs_normalized
}
