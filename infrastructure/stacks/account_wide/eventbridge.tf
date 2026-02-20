resource "aws_cloudwatch_event_rule" "mtls_secret_rotation_schedule" {
  count               = local.is_primary_environment ? 1 : 0
  name                = "${local.account_prefix}-mtls-rotation-schedule"
  schedule_expression = "rate(${var.mtls_secret_rotation_days} days)"
}

resource "aws_cloudwatch_event_target" "mtls_rotation_cert" {
  count     = local.is_primary_environment ? 1 : 0
  rule      = aws_cloudwatch_event_rule.mtls_secret_rotation_schedule[0].name
  target_id = "mtls-rotate-cert"
  arn       = aws_ssm_document.mtls_secret_rotation_runbook[0].arn
  role_arn  = aws_iam_role.mtls_rotation_schedule[0].arn

  input = jsonencode({
    DocumentName = aws_ssm_document.mtls_secret_rotation_runbook[0].name
    Parameters = {
      AutomationAssumeRole = [aws_iam_role.mtls_rotation_automation[0].arn]
      SecretId             = [aws_secretsmanager_secret.api_ca_cert_secret[0].id]
    }
  })
}

resource "aws_cloudwatch_event_target" "mtls_rotation_pk" {
  count     = local.is_primary_environment ? 1 : 0
  rule      = aws_cloudwatch_event_rule.mtls_secret_rotation_schedule[0].name
  target_id = "mtls-rotate-pk"
  arn       = aws_ssm_document.mtls_secret_rotation_runbook[0].arn
  role_arn  = aws_iam_role.mtls_rotation_schedule[0].arn

  input = jsonencode({
    DocumentName = aws_ssm_document.mtls_secret_rotation_runbook[0].name
    Parameters = {
      AutomationAssumeRole = [aws_iam_role.mtls_rotation_automation[0].arn]
      SecretId             = [aws_secretsmanager_secret.api_ca_pk_secret[0].id]
    }
  })
}
