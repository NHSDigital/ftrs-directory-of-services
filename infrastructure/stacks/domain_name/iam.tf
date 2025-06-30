resource "aws_iam_role" "route53_cross_account_role" {
  count = var.environment == "mgmt" ? 1 : 0
  name  = local.domain_cross_account_role

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = [
            for account in var.aws_accounts : data.aws_ssm_parameter.account_id[account].value
          ]
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "route53_cross_account_policy" {
  count       = var.environment == "mgmt" ? 1 : 0
  name        = local.domain_cross_account_role
  description = "Allow cross-account updates to root hosted zone records"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "route53:GetHostedZone",
          "route53:ChangeResourceRecordSets",
          "route53:ListHostedZones",
          "route53:ListTagsForResource"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "route53_cross_account_policy_attachment" {
  count      = var.environment == "mgmt" ? 1 : 0
  role       = aws_iam_role.route53_cross_account_role[0].name
  policy_arn = aws_iam_policy.route53_cross_account_policy[0].arn
}
