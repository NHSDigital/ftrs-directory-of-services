// IAM policy to allow the GitHub app runner to create/manage the JMeter EC2 IAM role and instance profile
// Scopes permissions to names that include "-jmeter" under this account and project/environment

// Caller/account context
// Removed duplicate aws_caller_identity data source; using the shared definition from common/provider.tf

// Role name to attach this policy to (matches error: ftrs-directory-of-services-app-github-runner)
// Adjust if your runner role is environment-specific
locals {
  target_app_runner_role_name = "${var.repo_name}-${var.app_github_runner_role_name}"
}

# trivy:ignore:AVD-AWS-0342 : PassRole is required for EC2 to assume the jmeter role; scope limited to EC2 and jmeter-specific ARNs
resource "aws_iam_policy" "app_github_runner_jmeter_iam" {
  name        = "${local.account_prefix}-app-gh-jmeter-iam"
  description = "Allow app GitHub runner to create/manage JMeter EC2 role & instance profile (scoped to -jmeter names)"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "JmeterInstanceProfileCRUD",
        Effect = "Allow",
        Action = [
          "iam:CreateInstanceProfile",
          "iam:DeleteInstanceProfile",
          "iam:GetInstanceProfile",
          "iam:TagInstanceProfile",
          "iam:UntagInstanceProfile"
        ],
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:instance-profile/${var.project}-${var.environment}-*-jmeter*"
        ]
      },
      {
        Sid    = "JmeterRoleCRUD",
        Effect = "Allow",
        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:GetRole",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:PutRolePermissionsBoundary",
          "iam:DeleteRolePermissionsBoundary"
        ],
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project}-${var.environment}-*-jmeter*"
        ]
      },
      {
        Sid    = "AssociateRoleWithInstanceProfile",
        Effect = "Allow",
        Action = [
          "iam:AddRoleToInstanceProfile",
          "iam:RemoveRoleFromInstanceProfile"
        ],
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:instance-profile/${var.project}-${var.environment}-*-jmeter*"
        ]
      },
      {
        Sid    = "AttachManagedPoliciesToRole",
        Effect = "Allow",
        Action = [
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy"
        ],
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project}-${var.environment}-*-jmeter*"
        ]
      },
      {
        Sid    = "ManageInlineRolePolicies",
        Effect = "Allow",
        Action = [
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:GetRolePolicy",
          "iam:ListRolePolicies"
        ],
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project}-${var.environment}-*-jmeter*"
        ]
      },
      {
        Sid    = "PassRoleToEC2",
        Effect = "Allow",
        Action = [
          "iam:PassRole"
        ],
        Resource = [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project}-${var.environment}-*-jmeter*"
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

resource "aws_iam_role_policy_attachment" "attach_app_runner_jmeter_iam" {
  role       = local.target_app_runner_role_name
  policy_arn = aws_iam_policy.app_github_runner_jmeter_iam.arn
}
