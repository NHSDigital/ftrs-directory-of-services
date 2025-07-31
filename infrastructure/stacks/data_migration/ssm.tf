resource "aws_ssm_parameter" "rds_event_listener_workspace_sqs_id" {
  name  = "${var.sqs_ssm_path_for_ids}${local.resource_prefix}-sqs-param-${local.workspace_suffix}"
  type  = "String"
  value = aws_sqs_queue.rds_event_listener.id
}
