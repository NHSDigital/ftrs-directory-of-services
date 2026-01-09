data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "appconfig_data_read" {
  statement {
    sid = "AppConfigDataRead"
    actions = [
      "appconfig:GetLatestConfiguration",
      "appconfig:StartConfigurationSession",
    ]
    resources = [
      "arn:aws:appconfig:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:application/${module.app_config.application_id}/environment/*/configuration/*"
    ]
  }
}
