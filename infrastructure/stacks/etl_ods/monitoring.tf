################################################################################
# CloudWatch Monitoring Module for ETL ODS Lambdas
################################################################################

module "etl_ods_lambda_monitoring" {
  source = "../../modules/cloudwatch-monitoring"

  resource_prefix   = local.resource_prefix
  sns_topic_name    = local.alarms_topic_name
  sns_display_name  = "ETL ODS Lambda Alarms"
  kms_key_id        = data.aws_kms_key.sns_kms_key.arn
  alarm_config_path = "lambda/config"

  # Enable Slack notifications
  slack_notifier_enabled       = true
  slack_notifier_function_name = "${local.project_prefix}-slack-notifier"

  monitored_resources = {
    extractor   = module.extractor_lambda.lambda_function_name
    transformer = module.transformer_lambda.lambda_function_name
    consumer    = module.consumer_lambda.lambda_function_name
  }

  resource "aws_cloudwatch_log_metric_filter" "extractor_lambda_start_time_metric" {
    name           = "${module.extractor_lambda.lambda_function_name}-start-timestamp"
    pattern        = "{ $.reference = \"ETL_EXTRACTOR_START\" }"
    log_group_name = aws_cloudwatch_log_group.application.name

    metric_transformation {
      name      = "ExtractorStart"
      namespace = "ODS/ETL"
      value     = "$.timestamp"
      unit      = "None"
      dimensions = {
        correlation_id = "$.correlation_id"
      }
    }
  }
}
