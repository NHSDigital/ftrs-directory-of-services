data "aws_iam_policy" "power_user_iam_policy" {
  name = "PowerUserAccess"
}

resource "aws_iam_role_policy_attachment" "power_user_iam_role_policy_attachment" {
  role       = aws_iam_role.github_runner_iam_role.name
  policy_arn = data.aws_iam_policy.power_user_iam_policy.arn
}

resource "aws_iam_policy" "read_only_user_iam_policy" {
  name        = "${var.repo_name}-github-runner-iam-services"
  description = "Read-only policy for IAM permissions required by GitHub runner"
  policy      = <<-EOF
  {
    "Version":"2012-10-17",
    "Statement": [
      {
          "Action": [
              "iam:GenerateCredentialReport",
              "iam:List*",
              "iam:GenerateServiceLastAccessedDetails",
              "iam:TagRole",
              "iam:DeletePolicy",
              "iam:CreateRole",
              "iam:DeleteRole",
              "iam:AttachRolePolicy",
              "iam:TagPolicy",
              "iam:CreatePolicy",
              "iam:PassRole",
              "iam:Get*",
              "iam:DetachRolePolicy",
              "iam:SimulatePrincipalPolicy",
              "iam:SimulateCustomPolicy",
              "iam:CreatePolicyVersion",
              "iam:DeletePolicyVersion",
              "iam:TagOpenIDConnectProvider",
              "iam:DeleteRolePolicy",
              "iam:PutRolePolicy",
              "iam:UpdateOpenIDConnectProviderThumbprint",
              "iam:UntagPolicy",
              "iam:UntagRole"
          ],
          "Effect": "Allow",
          "Resource": "*",
          "Sid": "ReadOnlyIAM"
      }
    ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "read_only_user_iam_role_policy_attachment" {
  role       = aws_iam_role.github_runner_iam_role.name
  policy_arn = aws_iam_policy.read_only_user_iam_policy.arn
}

resource "aws_iam_role" "github_runner_iam_role" {
  name               = "${var.repo_name}-${var.github_runner_role_name}"
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
