resource "aws_security_group" "version_history_lambda_security_group" {
  # checkov:skip=CKV2_AWS_5: False positive due to module reference
  count = var.version_history_enabled ? 1 : 0

  name        = "${local.resource_prefix}-version-history-lambda-sg${local.workspace_suffix}"
  description = "Security group for version history lambda"

  vpc_id = data.aws_vpc.vpc.id
}
