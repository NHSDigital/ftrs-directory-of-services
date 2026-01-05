resource "aws_ssm_parameter" "rds_event_listener_workspace_sqs_id" {
  # checkov:skip=CKV2_AWS_34: Needs to be encrypted
  count = local.is_primary_environment ? 1 : 0
  name  = "${var.sqs_ssm_path_for_ids}${var.environment}/${local.resource_prefix}-sqs-param"
  type  = "String"
  value = aws_sqs_queue.dms_event_queue.id
}
