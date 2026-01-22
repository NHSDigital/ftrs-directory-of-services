# WAFv2 Web ACL for DoS Search API Gateway (REGIONAL)
# Mirrors the complex/live DoS WAF ruleset (synthetic monitoring allowlists + geo + managed groups + logging).

locals {
  waf_web_acl_name   = "${local.resource_prefix}-dos-search-waf-web-acl${local.workspace_suffix}"
  waf_logs_log_group = "/aws/wafv2/${local.resource_prefix}-dos-search-waf${local.workspace_suffix}"
  # Note: WAF requires a metric_name value in visibility_config even when CloudWatch metrics are disabled.
  waf_metric_base_name  = "${local.resource_prefix}-dos-search-waf${local.workspace_suffix}"
  waf_allowed_countries = var.waf_allowed_country_codes

  # Synthetic monitoring allowlists are optional.
  # If CIDR lists are empty, we do not create the IP sets or the allow rules.
  enable_pingdom_allowlist    = length(var.waf_pingdom_ipv4_cidrs) > 0
  enable_statuscake_allowlist = length(var.waf_statuscake_ipv4_cidrs) > 0
}

resource "aws_cloudwatch_log_group" "waf_log_group" {
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  name              = local.waf_logs_log_group
  retention_in_days = var.waf_log_retention_days
}

resource "aws_wafv2_ip_set" "pingdom_ips" {
  count              = local.enable_pingdom_allowlist ? 1 : 0
  name               = "${local.resource_prefix}-dos-search-waf-pingdom-ips${local.workspace_suffix}"
  description        = "Pingdom synthetic monitoring source IPs"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = var.waf_pingdom_ipv4_cidrs
}

resource "aws_wafv2_ip_set" "statuscake_ips" {
  count              = local.enable_statuscake_allowlist ? 1 : 0
  name               = "${local.resource_prefix}-dos-search-waf-statuscake-ips${local.workspace_suffix}"
  description        = "StatusCake synthetic monitoring source IPs"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = var.waf_statuscake_ipv4_cidrs
}

resource "aws_wafv2_web_acl" "dos_search_web_acl" {
  name        = local.waf_web_acl_name
  description = "DoS Search API Gateway WAF (regional)"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # Synthetic monitoring allow rules (optional).
  # Note: these allowlisted sources bypass geo / managed rules.
  # Logging is enabled via aws_wafv2_web_acl_logging_configuration; metrics are intentionally disabled.
  dynamic "rule" {
    for_each = local.enable_pingdom_allowlist ? [1] : []
    content {
      name     = "dos-search-waf-allow-pingdom"
      priority = 0

      action {
        allow {}
      }

      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.pingdom_ips[0].arn
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = false
        metric_name                = "dos-search-waf-allow-pingdom"
        sampled_requests_enabled   = true
      }
    }
  }

  dynamic "rule" {
    for_each = local.enable_statuscake_allowlist ? [1] : []
    content {
      name     = "dos-search-waf-allow-statuscake"
      priority = 1

      action {
        allow {}
      }

      statement {
        ip_set_reference_statement {
          arn = aws_wafv2_ip_set.statuscake_ips[0].arn
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = false
        metric_name                = "dos-search-waf-allow-statuscake"
        sampled_requests_enabled   = true
      }
    }
  }

  # Geo restrictions
  # Block requests that are NOT from allowed countries
  rule {
    name     = "dos-search-waf-block-disallowed-countries"
    priority = 2

    action {
      block {}
    }

    statement {
      not_statement {
        statement {
          geo_match_statement {
            country_codes = local.waf_allowed_countries
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "dos-search-waf-block-disallowed-countries"
      sampled_requests_enabled   = true
    }
  }

  # Optional hostile country block (higher priority than managed groups)
  dynamic "rule" {
    for_each = length(var.waf_hostile_country_codes) > 0 ? [1] : []
    content {
      name     = "dos-search-waf-block-hostile-countries"
      priority = 3

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
        metric_name                = "dos-search-waf-block-hostile-countries"
        sampled_requests_enabled   = true
      }
    }
  }

  # Managed rule groups with overrides (mirrors live configuration intent)
  rule {
    name     = "AWSManagedIPReputationList"
    priority = 10

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedIPReputationList"
        vendor_name = "AWS"

        rule_action_override {
          name = "AWSManagedIPReputationList"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "AWSManagedReconnaissanceList"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "AWSManagedIPDDoSList"
          action_to_use {
            count {}
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "dos-search-waf-aws-managed-ip-reputation-list"
      sampled_requests_enabled   = true
    }
  }

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

        # Override all rule actions (selected high-signal rules)
        rule_action_override {
          name = "JavaDeserializationRCE_BODY"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "JavaDeserializationRCE_URIPATH"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "JavaDeserializationRCE_QUERYSTRING"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "JavaDeserializationRCE_HEADER"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "Host_localhost_HEADER"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "PROPFIND_METHOD"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "ExploitablePaths_URIPATH"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "Log4JRCE_QUERYSTRING"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "Log4JRCE_BODY"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "Log4JRCE_URIPATH"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "Log4JRCE_HEADER"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "ReactJSRCE_BODY"
          action_to_use {
            block {}
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "dos-search-waf-aws-managed-known-bad-inputs"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWSManagedRulesBotControlRuleSet"
    priority = 30

    # Bot Control is run in COUNT mode at the rule-group level, with selected bot categories/signals overridden to BLOCK.
    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesBotControlRuleSet"
        vendor_name = "AWS"

        # Block selected bot categories/signals; all other Bot Control detections are counted.
        rule_action_override {
          name = "CategoryAdvertising"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategoryArchiver"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategoryContentFetcher"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategoryEmailClient"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategoryHttpLibrary"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategoryLinkChecker"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategoryMiscellaneous"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategoryMonitoring"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategoryScrapingFramework"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategorySearchEngine"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategorySecurity"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategorySeo"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategorySocialMedia"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CategoryAI"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "SignalAutomatedBrowser"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "SignalKnownBotDataCenter"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "SignalNonBrowserUserAgent"
          action_to_use {
            block {}
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "dos-search-waf-aws-managed-bot-control"
      sampled_requests_enabled   = true
    }
  }

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

        # Override all rule actions (selected high-signal rules)
        rule_action_override {
          name = "NoUserAgent_HEADER"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "UserAgent_BadBots_HEADER"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "SizeRestrictions_QUERYSTRING"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "SizeRestrictions_Cookie_HEADER"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "SizeRestrictions_BODY"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "SizeRestrictions_URIPATH"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "EC2MetaDataSSRF_BODY"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "EC2MetaDataSSRF_COOKIE"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "EC2MetaDataSSRF_URIPATH"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "EC2MetaDataSSRF_QUERYARGUMENTS"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "GenericLFI_QUERYARGUMENTS"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "GenericLFI_URIPATH"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "GenericLFI_BODY"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "RestrictedExtensions_URIPATH"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "RestrictedExtensions_QUERYARGUMENTS"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "GenericRFI_QUERYARGUMENTS"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "GenericRFI_BODY"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "GenericRFI_URIPATH"
          action_to_use {
            block {}
          }
        }

        rule_action_override {
          name = "CrossSiteScripting_COOKIE"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CrossSiteScripting_QUERYARGUMENTS"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CrossSiteScripting_BODY"
          action_to_use {
            block {}
          }
        }
        rule_action_override {
          name = "CrossSiteScripting_URIPATH"
          action_to_use {
            block {}
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "dos-search-waf-aws-managed-common-rules"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = false
    metric_name                = local.waf_metric_base_name
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_web_acl_logging_configuration" "dos_search_waf_logging" {
  log_destination_configs = [aws_cloudwatch_log_group.waf_log_group.arn]
  resource_arn            = aws_wafv2_web_acl.dos_search_web_acl.arn
}

resource "aws_wafv2_web_acl_association" "dos_search_api_gateway_stage" {
  resource_arn = aws_api_gateway_stage.default.arn
  web_acl_arn  = aws_wafv2_web_acl.dos_search_web_acl.arn
}
