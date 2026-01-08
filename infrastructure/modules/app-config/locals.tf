locals {
  iam_policy_default_name                   = "${var.name}-appconfig-data-read"
  iam_policy_default_description            = "Allows AppConfig data session and configuration fetch"
  appconfig_lambda_extension_aws_account_id = "282860088358" # gitleaks:allow
  appconfig_extension_layer_arn             = "arn:aws:lambda:${var.aws_region}:${local.appconfig_lambda_extension_aws_account_id}:layer:AWS-AppConfig-Extension:207"
}
