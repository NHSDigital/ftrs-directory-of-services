################################################################################
# CloudWatch Monitoring Module for ETL ODS Lambdas
################################################################################

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
