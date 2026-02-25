resource "aws_scheduler_schedule_group" "etl_schedule_group" {
  name = "${local.resource_prefix}-etl-schedule-group${local.workspace_suffix}"
}

resource "aws_scheduler_schedule" "ods_etl_schedule" {

  name        = "${local.resource_prefix}-ods-etl-schedule${local.workspace_suffix}"
  group_name  = aws_scheduler_schedule_group.etl_schedule_group.name
  description = "Schedule to trigger the ODS ETL extractor lambda"
  state       = local.is_primary_environment ? "ENABLED" : "DISABLED"
  kms_key_arn = data.aws_kms_key.scheduler_kms_key.arn

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(10 2 * * ? *)" # At 02:10 AM every day
  schedule_expression_timezone = "Europe/London"

  target {
    arn      = module.extractor_lambda.lambda_function_arn
    role_arn = aws_iam_role.ods_etl_scheduler_invoke_role.arn

    input = jsonencode({ "is_scheduled" = true })

    retry_policy {
      maximum_event_age_in_seconds = 43200
      maximum_retry_attempts       = 90
    }
  }
}
