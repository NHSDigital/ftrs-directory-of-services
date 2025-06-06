locals {
  account_github_runner_policy = jsondecode(templatefile("${path.module}/account_github_runner_policy.json.tpl", {
    project   = var.project
    repo_name = var.repo_name
  }))

  app_github_runner_policy = jsondecode(templatefile("${path.module}/app_github_runner_policy.json.tpl", {
    project   = var.project
    repo_name = var.repo_name
  }))
}

resource "aws_iam_role" "account_github_runner_role" {
  name = "${var.repo_name}-${var.account_github_runner_role_name}"

  assume_role_policy = <<EOF
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Effect":"Allow",
      "Principal":{
        "Federated":"arn:aws:iam::${local.account_id}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action":"sts:AssumeRoleWithWebIdentity",
      "Condition":{
        "ForAllValues:StringLike":{
          "token.actions.githubusercontent.com:sub":"repo:${var.github_org}/${var.repo_name}:*",
          "token.actions.githubusercontent.com:aud":"sts.amazonaws.com"
        }
      }
    }
  ]
}
EOF
}

resource "aws_iam_role" "app_github_runner_role" {
  name = "${var.repo_name}-${var.app_github_runner_role_name}"

  assume_role_policy = <<EOF
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Effect":"Allow",
      "Principal":{
        "Federated":"arn:aws:iam::${local.account_id}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action":"sts:AssumeRoleWithWebIdentity",
      "Condition":{
        "ForAllValues:StringLike":{
          "token.actions.githubusercontent.com:sub":"repo:${var.github_org}/${var.repo_name}:*",
          "token.actions.githubusercontent.com:aud":"sts.amazonaws.com"
        }
      }
    }
  ]
}
EOF
}

resource "aws_iam_policy" "account_github_runner_policy" {
  name        = "${var.repo_name}-${var.account_github_runner_role_name}"
  description = "IAM policy for Account GitHub Actions runner"
  policy      = jsonencode(local.account_github_runner_policy)
}

resource "aws_iam_policy" "app_github_runner_policy" {
  name        = "${var.repo_name}-${var.app_github_runner_role_name}"
  description = "IAM policy for App GitHub Actions runner"
  policy      = jsonencode(local.app_github_runner_policy)
}

resource "aws_iam_role_policy_attachment" "account_github_runner_policy_attachment" {
  role       = aws_iam_role.account_github_runner_role.name
  policy_arn = aws_iam_policy.account_github_runner_policy.arn
}

resource "aws_iam_role_policy_attachment" "app_github_runner_policy_attachment" {
  role       = aws_iam_role.app_github_runner_role.name
  policy_arn = aws_iam_policy.app_github_runner_policy.arn
}
