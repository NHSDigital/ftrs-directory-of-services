locals {
  sns_topic_name = "${local.resource_prefix}-alarms${local.workspace_suffix}"
  lambda_s3_key  = "${local.artefact_base_path}/${var.project}-slack-notifier-lambda.zip"
}
