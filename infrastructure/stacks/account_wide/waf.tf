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
# - Default action allows; managed rules count in dev and block in non-dev.
# - Dev count mode is a common industry pattern to avoid blocking automated test traffic (e.g., GitHub runners).
# - APIM/Apigee and EC2/NAT allowlist rules are count-only for visibility.
# - Managed rule groups exclude the combined allowlist via scope-down.
# - Allowlist rules/IP sets only exist when their CIDR lists are non-empty.
resource "aws_wafv2_web_acl" "regional_waf_web_acl" {
  # checkov:skip=CKV_AWS_192: False positive due to dynamic blocks and scope-down logic in this Web ACL.
  name        = "${local.resource_prefix}-${var.regional_waf_name}"
  description = "Regional WAF Web ACL"
  scope       = var.regional_waf_scope

  default_action {
    allow {}
  }

  dynamic "rule" {
    for_each = local.apim_apigee_allowlist_enabled ? [1] : []
    content {
      name     = "allow-apim-apigee-cidrs"
      priority = 5

      action {
        count {}
      }

      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.apim_apigee_whitelist_regional[0].arn
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = false
        metric_name                = "${local.resource_prefix}-regional-allow-apim-apigee"
        sampled_requests_enabled   = false
      }
    }
  }

  dynamic "rule" {
    for_each = local.ec2_allowlist_enabled ? [1] : []
    content {
      name     = "allow-ec2-whitelist-regional"
      priority = 6

      action {
        count {}
      }

      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.ec2_whitelist_regional[0].arn
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = false
        metric_name                = "${local.resource_prefix}-regional-allow-ec2"
        sampled_requests_enabled   = false
      }
    }
  }

  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 10

    dynamic "override_action" {
      for_each = var.environment == "dev" ? [1] : []
      content {
        count {}
      }
    }

    dynamic "override_action" {
      for_each = var.environment == "dev" ? [] : [1]
      content {
        none {}
      }
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"

        dynamic "scope_down_statement" {
          for_each = local.regional_allowlist_enabled ? [1] : []
          content {
            not_statement {
              statement {
                ip_set_reference_statement {
                  arn = aws_wafv2_ip_set.regional_allowlist[0].arn
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.resource_prefix}-regional-waf-aws-managed-known-bad-inputs"
      sampled_requests_enabled   = false
    }
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 20

    dynamic "override_action" {
      for_each = var.environment == "dev" ? [1] : []
      content {
        count {}
      }
    }

    dynamic "override_action" {
      for_each = var.environment == "dev" ? [] : [1]
      content {
        none {}
      }
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"

        dynamic "scope_down_statement" {
          for_each = local.regional_allowlist_enabled ? [1] : []
          content {
            not_statement {
              statement {
                ip_set_reference_statement {
                  arn = aws_wafv2_ip_set.regional_allowlist[0].arn
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.resource_prefix}-regional-waf-aws-managed-common-rules"
      sampled_requests_enabled   = false
    }
  }

  rule {
    name     = "AWSManagedRulesLinuxRuleSet"
    priority = 30

    dynamic "override_action" {
      for_each = var.environment == "dev" ? [1] : []
      content {
        count {}
      }
    }

    dynamic "override_action" {
      for_each = var.environment == "dev" ? [] : [1]
      content {
        none {}
      }
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesLinuxRuleSet"
        vendor_name = "AWS"

        dynamic "scope_down_statement" {
          for_each = local.regional_allowlist_enabled ? [1] : []
          content {
            not_statement {
              statement {
                ip_set_reference_statement {
                  arn = aws_wafv2_ip_set.regional_allowlist[0].arn
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.resource_prefix}-regional-waf-aws-managed-linux-rules"
      sampled_requests_enabled   = false
    }
  }

  rule {
    name     = "AWSManagedRulesUnixRuleSet"
    priority = 40

    dynamic "override_action" {
      for_each = var.environment == "dev" ? [1] : []
      content {
        count {}
      }
    }

    dynamic "override_action" {
      for_each = var.environment == "dev" ? [] : [1]
      content {
        none {}
      }
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesUnixRuleSet"
        vendor_name = "AWS"

        dynamic "scope_down_statement" {
          for_each = local.regional_allowlist_enabled ? [1] : []
          content {
            not_statement {
              statement {
                ip_set_reference_statement {
                  arn = aws_wafv2_ip_set.regional_allowlist[0].arn
                }
              }
            }
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${local.resource_prefix}-regional-waf-aws-managed-unix-rules"
      sampled_requests_enabled   = false
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${local.resource_prefix}-regional-waf"
    sampled_requests_enabled   = false
  }
}

resource "aws_wafv2_ip_set" "ec2_whitelist_regional" {
  count              = local.ec2_allowlist_enabled ? 1 : 0
  name               = "${local.resource_prefix}-ec2-whitelist-regional"
  description        = "IP set for EC2 egress via NAT gateway public EIPs (regional scope)"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"

  addresses = local.ec2_allowlist_cidrs
}

resource "aws_wafv2_ip_set" "apim_apigee_whitelist_regional" {
  count              = local.apim_apigee_allowlist_enabled ? 1 : 0
  name               = "${local.resource_prefix}-apim-apigee-whitelist-regional"
  description        = "IP set for APIM/Apigee allowlist (regional scope)"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"

  addresses = local.apim_apigee_allowlist_cidrs
}

resource "aws_wafv2_ip_set" "regional_allowlist" {
  count              = local.regional_allowlist_enabled ? 1 : 0
  name               = "${local.resource_prefix}-regional-allowlist"
  description        = "Combined allowlist for APIM/Apigee and EC2/NAT (regional scope)"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"

  addresses = local.regional_allowlist_cidrs
}
