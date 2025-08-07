resource "aws_cloudwatch_event_rule" "dms_full_replication_task_completed" {
  name        = "${local.resource_prefix}-etl-full-replication-task-completed"
  description = "Trigger Lambda on DMS full replication task completion"
  event_pattern = jsonencode({
    "source" : ["aws.dms"],
    "detail-type" : ["DMS Replication Task State Change"],
    "detail" : {
      "ReplicationTaskId" : ["${aws_dms_replication_task.dms_full_replication_task[0].replication_task_id}"],
      "Status" : ["completed"]
    }
  })
}

# resource "aws_cloudwatch_event_target" "dms_full_replication_task_lambda" {
#   rule      = aws_cloudwatch_event_rule.dms_full_replication_task_completed.name
#   arn       = //FIXME Add Tom Lambda handler arn here
#   # You can add input/transform here if needed
# }

# resource "aws_lambda_permission" "allow_eventbridge_invoke" {
#   statement_id  = "AllowExecutionFromEventBridge"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.dms_task_completion_handler.function_name
#   principal     = "events.amazonaws.com"
#   source_arn    = aws_cloudwatch_event_rule.dms_full_replication_task_completed.arn
# }
