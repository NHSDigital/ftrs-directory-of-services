locals {
  iam_policy_default_name          = "${var.name}-appconfig-data-read"
  iam_policy_default_description   = "Allows AppConfig data session and configuration fetch"
  use_hosted_configuration         = true
  deployment_configuration_version = "1"
}
