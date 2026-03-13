resource "aws_lambda_layer_version" "common_packages_layer" {
  layer_name          = "${local.resource_prefix}-common-packages-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common packages for Lambda functions"

  s3_bucket         = local.artefacts_bucket
  s3_key            = "${local.artefact_base_path}/${var.project}-python-packages-layer.zip"
  s3_object_version = data.aws_s3_object.common_packages_layer.version_id
}

resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.resource_prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket         = local.artefacts_bucket
  s3_key            = "${local.artefact_base_path}/${var.project}-${var.stack_name}-python-dependency-layer.zip"
  s3_object_version = data.aws_s3_object.python_dependency_layer.version_id
}
