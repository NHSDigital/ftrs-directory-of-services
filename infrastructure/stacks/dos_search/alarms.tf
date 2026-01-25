module "sns" {
  source = "../../modules/sns"

  topic_name   = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}"
  display_name = "DoS Search Lambda Alarms"
  kms_key_id   = local.kms_aliases.sqs

  tags = {
    Name = "${local.resource_prefix}-lambda-alarms${local.workspace_suffix}"
  }
}
