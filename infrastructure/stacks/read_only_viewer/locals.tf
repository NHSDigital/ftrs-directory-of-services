locals {
  workspace_suffix = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  custom_rules = [
    {
      name     = "allowed-countries-rule"
      priority = 102
      action   = "block"
      not_statement = {
        geo_match_statement = {
          country_codes : ["GB"]
          forwarded_ip_config = {
            fallback_behavior = "NO_MATCH"
            header_name       = "X-Forwarded-For"
          }
        }
      }
      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "allowed-countries-rule"
        sampled_requests_enabled   = true
      }
    },
    {
      name     = "rate-limit-rule"
      priority = 101
      action   = "block"
      rate_based_statement = {
        limit                 = 100
        aggregate_key_type    = "FORWARDED_IP"
        evaluation_window_sec = 120
        forwarded_ip_config = {
          fallback_behavior = "NO_MATCH"
          header_name       = "X-Forwarded-For"
        }
      }
      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = "rate-limit-rule"
        sampled_requests_enabled   = true
      }
    },
    {
      name     = "vpn-restriction-rule"
      priority = 100
      action   = "block"
      not_statement = {
        ip_set_reference_statement = {
          arn = module.read_only_viewer_ip_set.aws_wafv2_ip_set_arn
        }
      }
      visibility_config = {
        cloudwatch_metrics_enabled = false
        metric_name                = "cloudwatch_metric_name"
        sampled_requests_enabled   = false
      }

    }
  ]

  aws_managed_waf_rules = [
    for i, rule in local.aws_managed_rules : {
      name     = rule
      priority = i

      override_action = {
        none = {}
      }

      statement = {
        managed_rule_group_statement = {
          name        = rule
          vendor_name = "AWS"
        }
      }

      visibility_config = {
        cloudwatch_metrics_enabled = true
        metric_name                = rule
        sampled_requests_enabled   = true
      }
    }
  ]

  aws_managed_rules = [
    "AWSManagedRulesCommonRuleSet",
    "AWSManagedRulesKnownBadInputsRuleSet",
    "AWSManagedRulesAmazonIpReputationList",
    "AWSManagedRulesAnonymousIpList",
    "AWSManagedRulesAdminProtectionRuleSet",
  ]
  waf_rules = concat(local.aws_managed_waf_rules, local.custom_rules)
}
