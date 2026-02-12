locals {
  resource_prefix  = "${var.project}-slack-notifier"
  account_prefix   = split("-", data.aws_caller_identity.current.account_id)[0]
  artefacts_bucket = var.artefacts_bucket_name
  lambda_s3_key    = var.lambda_artifact_key
}
