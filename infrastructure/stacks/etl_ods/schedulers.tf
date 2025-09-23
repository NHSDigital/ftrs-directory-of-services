resource "aws_scheduler_schedule_group" "etl_schedule_group" {

  name = "${local.resource_prefix}-etl-schedule-group${local.workspace_suffix}"

}


# checkov:skip=CKV_AWS_297: TODO Determine if we need a KMS key for Scheduler
resource "aws_scheduler_schedule" "ods_etl_schedule" {
  name        = "${local.resource_prefix}-ods-etl-schedule${local.workspace_suffix}"
  group_name  = aws_scheduler_schedule_group.etl_schedule_group.name
  description = "Schedule to trigger the ODS ETL processor lambda"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(15 * * * ? *)" # At minute 15 past every hour
  schedule_expression_timezone = "Europe/London"

  target {
    arn      = module.processor_lambda.lambda_function_arn
    role_arn = aws_iam_role.ods_etl_scheduler_invoke_role.arn

    input = jsonencode({
      "date" = "${formatdate("YYYY-MM-DD", timestamp())}"
    })

    retry_policy {
      maximum_event_age_in_seconds = 43200
      maximum_retry_attempts       = 90
    }
  }
}
