data "aws_iam_policy_document" "appconfig_data_read" {
  statement {
    sid = "AppConfigDataRead"
    actions = [
      "appconfig:GetLatestConfiguration",
      "appconfig:StartConfigurationSession",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "appconfig_data_read" {
  count = var.create_iam_policy ? 1 : 0

  name        = coalesce(var.iam_policy_name, local.iam_policy_default_name)
  description = coalesce(var.iam_policy_description, local.iam_policy_default_description)
  policy      = data.aws_iam_policy_document.appconfig_data_read.json
}
