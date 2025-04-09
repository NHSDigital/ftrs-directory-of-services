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

# dependency between stacks so add if needed post creation
# TODO review permissions generally to remove power user and adopt with least privilege
# resource "aws_iam_policy" "access_policy_s3" {
#   name        = "${var.repo_name}-github-runner-s3-access"
#   description = "Policies to access artefact bucket in mgmt account"
#   policy      = <<-EOF
#   {
#     "Version":"2012-10-17",
#     "Statement": [

#         {
#             "Action": "s3:*",
#             "Effect": "Allow",
#             "Resource": "*",
#             "Sid": "VisualEditor5"
#         },

#         {
#             "Effect": "Allow",
#             "Action": "s3:ListBucket",
#             "Resource": [
#               "${data.aws_s3_bucket.artefact_bucket.arn}",
#             ]
#         },
#         {
#             "Action": [
#                 "s3:GetObject",
#                 "s3:GetObjectTagging",
#                 "s3:DeleteObject",
#                 "s3:PutObject",
#                 "s3:PutObjectTagging"
#             ],
#             "Effect": "Allow",
#             "Resource": [
#               "${data.aws_s3_bucket.artefact_bucket.arn}",
#             ]
#         }
#     ]
#   }
#   EOF
# }

# resource "aws_iam_role_policy_attachment" "attach_s3_access" {
#   role       = aws_iam_role.github_runner_role.name
#   policy_arn = aws_iam_policy.access_policy_s3.arn
# }
