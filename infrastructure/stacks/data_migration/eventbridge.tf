resource "aws_cloudwatch_event_rule" "dms_full_replication_task_completed" {
  count = local.is_primary_environment ? 1 : 0

  name        = "${local.resource_prefix}-etl-full-replication-task-completed"
  description = "Trigger Lambda on DMS full replication task completion"
  event_pattern = jsonencode({
    "source" : ["aws.dms"],
    "detail" : {
      "category" : ["StateChange"],
      "eventId" : ["DMS-EVENT-0079"]
    }
  })
}

resource "aws_cloudwatch_event_target" "dms_full_replication_task_lambda" {
  count = local.is_primary_environment ? 1 : 0

  rule = aws_cloudwatch_event_rule.dms_full_replication_task_completed[0].name
  arn  = module.queue_populator_lambda[0].lambda_function_arn
}

resource "aws_lambda_permission" "eventbridge_lambda_permission" {
  count = local.is_primary_environment ? 1 : 0

  statement_id  = "AllowLambdaExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.queue_populator_lambda[0].lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.dms_full_replication_task_completed[0].arn
}
