# WAFv2 Web ACL for DoS Search API Gateway (REGIONAL)
# Implements geo restrictions, AWS managed rule groups, and WAF logging.

resource "aws_wafv2_web_acl" "dos_search_web_acl" {
  name        = "${local.resource_prefix}-dos-search-waf-web-acl${local.workspace_suffix}"
  description = "DOS Search API Gateway WAF regional"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # Geo restrictions
  # Count requests that are NOT from allowed countries (COUNT mode while tuning)
  # IMPORTANT: This rule implements a strict allow-list (default-deny) when set to BLOCK.
  # Here we run it in COUNT mode so operators can monitor what would be blocked before enforcing.
  # It matches requests that are NOT from values listed in `var.waf_allowed_country_codes`.
  # Do NOT deploy with `waf_allowed_country_codes` empty — that will either
  # (a) cause the Web ACL creation to fail or (b) effectively disable the intended default-deny
  # behaviour and allow traffic from all countries. Ensure tfvars provide at least one
  # country code (e.g. ["GB", "JE", "IM"]).
  rule {
    name     = "dos-search-waf-block-disallowed-countries"
    priority = 0

    action {
      count {}
    }

    statement {
      not_statement {
        statement {
          geo_match_statement {
            country_codes = var.waf_allowed_country_codes
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "${local.resource_prefix}-dos-search-waf-block-disallowed-countries${local.workspace_suffix}"
      sampled_requests_enabled   = true
    }
  }

  # Optional hostile country block (higher priority than managed groups)
  dynamic "rule" {
    for_each = length(var.waf_hostile_country_codes) > 0 ? [1] : []
    content {
      name     = "dos-search-waf-block-hostile-countries"
      priority = 1

      action {
        block {}
      }

      statement {
        geo_match_statement {
          country_codes = var.waf_hostile_country_codes
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = false
        metric_name                = "${local.resource_prefix}-dos-search-waf-block-hostile-countries${local.workspace_suffix}"
        sampled_requests_enabled   = true
      }
    }
  }

  # Managed rule groups
  # Note: WAFNonexistentItemException at CreateWebACL is commonly caused by referencing a managed rule group name
  # or per-rule override 'name' that doesn't exist in the target region/account.

  # IP Reputation (managed rules - run in normal mode)
  rule {
    name     = "AWSManagedRulesAmazonIpReputationList"
    priority = 10

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
      metric_name                = "${local.resource_prefix}-dos-search-waf-aws-managed-ip-reputation-list${local.workspace_suffix}"
      sampled_requests_enabled   = true
    }
  }

  # Known bad inputs (managed rules - run in normal mode)
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 20

    # Override rule group = false
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
      metric_name                = "${local.resource_prefix}-dos-search-waf-aws-managed-known-bad-inputs${local.workspace_suffix}"
      sampled_requests_enabled   = true
    }
  }

  # Bot Control (COUNT mode while tuning)
  rule {
    name     = "AWSManagedRulesBotControlRuleSet"
    priority = 30

    # Override rule group = true (rule group action set to COUNT)
    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesBotControlRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "${local.resource_prefix}-dos-search-waf-aws-managed-bot-control${local.workspace_suffix}"
      sampled_requests_enabled   = true
    }
  }

  # Common rules (COUNT mode while tuning)
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 40

    # Override rule group = true (rule group action set to COUNT)
    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "${local.resource_prefix}-dos-search-waf-aws-managed-common-rules${local.workspace_suffix}"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = false
    metric_name                = "${local.resource_prefix}-dos-search-waf${local.workspace_suffix}"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_web_acl_logging_configuration" "dos_search_waf_logging" {
  # Use the log group's ARN as the destination.
  log_destination_configs = [aws_cloudwatch_log_group.waf_log_group.arn]
  resource_arn            = aws_wafv2_web_acl.dos_search_web_acl.arn

  depends_on = [aws_cloudwatch_log_resource_policy.dos_search_waf_log_group_policy]
}
