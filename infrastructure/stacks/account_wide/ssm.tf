// SSM Automation runbook wiring for mTLS secret promotion (AWSPENDING -> AWSCURRENT).
// Triggered by EventBridge on a fixed interval: rate(${var.mtls_secret_rotation_days} days).
// Rotates: /${var.repo_name}/${var.environment}/api-ca-cert and /${var.repo_name}/${var.environment}/api-ca-pk.
// Created only in the primary environment (default workspace).

resource "aws_ssm_document" "mtls_secret_rotation_runbook" {
  count         = local.is_primary_environment ? 1 : 0
  name          = "${local.account_prefix}-mtls-promote-secret-version"
  document_type = "Automation"
  content       = file("${path.module}/templates/mtls_secret_rotation.yaml")
}

resource "aws_iam_role" "mtls_rotation_schedule" {
  count = local.is_primary_environment ? 1 : 0
  name  = "${local.account_prefix}-mtls-rotation-schedule"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "mtls_rotation_schedule" {
  count = local.is_primary_environment ? 1 : 0
  role  = aws_iam_role.mtls_rotation_schedule[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:StartAutomationExecution"
        ]
        Resource = aws_ssm_document.mtls_secret_rotation_runbook[0].arn
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = aws_iam_role.mtls_rotation_automation[0].arn
      }
    ]
  })
}
