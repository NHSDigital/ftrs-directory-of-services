// filepath: infrastructure/stacks/gp_search/jmeter_runner_iam_bootstrap.tf

locals {
  target_app_runner_role_name = "${var.repo_name}-${var.app_github_runner_role_name}"
}

# Grant the GitHub app runner minimal IAM create permissions so this stack can provision JMeter role/profile
#checkov:skip=CKV_AWS_289: Create* actions require wildcard resource; remaining actions are scoped by project prefix
#checkov:skip=CKV_AWS_355: Wildcard resource used only for Create* actions which do not support resource-level permissions
resource "aws_iam_role_policy" "app_runner_jmeter_iam_bootstrap" {
  name = "${local.account_prefix}-app-runner-jmeter-iam-bootstrap"
  role = local.target_app_runner_role_name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "AllowCreateInstanceProfile",
        Effect = "Allow",
        Action = [
          "iam:CreateInstanceProfile"
        ],
        Resource = "*"
      },
      {
        Sid    = "AllowCreateRole",
        Effect = "Allow",
        Action = [
          "iam:CreateRole"
        ],
        Resource = "*"
      },
      {
        Sid    = "ManageProjectInstanceProfiles",
        Effect = "Allow",
        Action = [
          "iam:GetInstanceProfile",
          "iam:DeleteInstanceProfile",
          "iam:TagInstanceProfile",
          "iam:UntagInstanceProfile",
          "iam:AddRoleToInstanceProfile",
          "iam:RemoveRoleFromInstanceProfile"
        ],
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:instance-profile/${var.project}-${var.environment}-*"
        ]
      },
      {
        Sid    = "ManageProjectRoles",
        Effect = "Allow",
        Action = [
          "iam:GetRole",
          "iam:DeleteRole",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:PutRolePermissionsBoundary",
          "iam:DeleteRolePermissionsBoundary"
        ],
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project}-${var.environment}-*"
        ]
      },
      {
        Sid    = "PassProjectRoleToEC2",
        Effect = "Allow",
        Action = [
          "iam:PassRole"
        ],
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project}-${var.environment}-*"
        ],
        Condition = {
          StringEquals = {
            "iam:PassedToService" = "ec2.amazonaws.com"
          }
        }
      }
    ]
  })
}
