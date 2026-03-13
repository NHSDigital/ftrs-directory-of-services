module "waf_monitoring" {
  # count = local.is_primary_environment ? 1 : 0 TODO: Enable once testing is complete
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix = local.resource_prefix

  sns_topic_name   = "${local.alarms_topic_name}-waf"
  sns_display_name = "DoS Search Alarms WAF"
  kms_key_id       = data.aws_kms_key.sns_kms_key.arn

  alarm_config_path = "waf/config"

  monitored_resources = {
    dos_search_waf = data.aws_wafv2_web_acl.regional.name
  }

  resource_extra_dimensions = {
    dos_search_waf = {
      "blocked-requests-warning"        = { Region = var.aws_region }
      "blocked-requests-critical"       = { Region = var.aws_region }
      "allowed-requests-spike-critical" = { Region = var.aws_region }
      "counted-requests-warning"        = { Region = var.aws_region }
    }
  }

  alarm_thresholds = {
    dos_search_waf = {
      "blocked-requests-warning"  = var.waf_blocked_requests_warning_threshold
      "blocked-requests-critical" = var.waf_blocked_requests_critical_threshold
    }
  }

  alarm_evaluation_periods = {
    dos_search_waf = {
      "blocked-requests-warning"  = var.waf_blocked_requests_warning_evaluation_periods
      "blocked-requests-critical" = var.waf_blocked_requests_critical_evaluation_periods
    }
  }

  alarm_periods = {
    dos_search_waf = {
      "blocked-requests-warning"  = var.waf_blocked_requests_period_seconds
      "blocked-requests-critical" = var.waf_blocked_requests_period_seconds
    }
  }

  enable_warning_alarms = var.enable_warning_alarms

  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  tags = {
    Name = local.alarms_topic_name
  }
}
