resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  filename         = "${path.module}/${var.project}-python-dependency-layer-${var.application_tag}.zip"
  source_code_hash = filebase64sha256("${path.module}/${var.project}-python-dependency-layer-${var.application_tag}.zip")
}
