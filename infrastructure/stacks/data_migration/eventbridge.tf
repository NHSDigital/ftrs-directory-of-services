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
# Commented out the queue populator related resources for now as for the first phase we need more control over data migration process.
/* resource "aws_cloudwatch_event_target" "dms_full_replication_task_queue_populator_lambda" {
  count = local.is_primary_environment ? 1 : 0

  rule      = aws_cloudwatch_event_rule.dms_full_replication_task_completed[0].name
  target_id = "queue-populator-lambda"
  arn       = module.queue_populator_lambda.lambda_function_arn

  dead_letter_config {
    arn = aws_sqs_queue.eventbridge_event_full_migration_completion_dlq[0].arn
  }
} */

resource "aws_cloudwatch_event_target" "dms_full_replication_task_dms_db_lambda" {
  count = local.is_primary_environment ? 1 : 0

  rule      = aws_cloudwatch_event_rule.dms_full_replication_task_completed[0].name
  target_id = "dms-db-lambda"
  arn       = module.dms_db_lambda[0].lambda_function_arn

  dead_letter_config {
    arn = aws_sqs_queue.eventbridge_event_full_migration_completion_dlq[0].arn
  }
}
# Commented out the queue populator related resources for now as for the first phase we need more control over data migration process.
/* resource "aws_lambda_permission" "eventbridge_queue_populator_lambda_permission" {
  count = local.is_primary_environment ? 1 : 0

  statement_id  = "AllowQueuePopulatorExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.queue_populator_lambda.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.dms_full_replication_task_completed[0].arn
} */

resource "aws_lambda_permission" "eventbridge_dms_db_lambda_permission" {
  count = local.is_primary_environment ? 1 : 0

  statement_id  = "AllowDmsDbLambdaExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.dms_db_lambda[0].lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.dms_full_replication_task_completed[0].arn
}
