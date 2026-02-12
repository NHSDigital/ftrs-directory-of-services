locals {
  resource_prefix_slack = "${var.project}-slack-notifier"
  lambda_s3_key         = var.lambda_artifact_key
}
