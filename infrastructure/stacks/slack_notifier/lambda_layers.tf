# Lambda layers for Slack notifier
resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  s3_bucket           = local.artefacts_bucket
  s3_key              = "${local.artefact_base_path}/${var.project}-slack-notifier-python-dependency-layer.zip"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Python dependencies for Slack notifier Lambda"
}

resource "aws_lambda_layer_version" "common_packages_layer" {
  layer_name          = "${local.resource_prefix}-common-packages-layer${local.workspace_suffix}"
  s3_bucket           = local.artefacts_bucket
  s3_key              = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python packages layer"
}
