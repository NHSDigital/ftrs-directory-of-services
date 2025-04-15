resource "aws_lambda_layer_version" "python_dependency_layer" {
  layer_name          = "${local.prefix}-python-dependency-layer${local.workspace_suffix}"
  compatible_runtimes = [var.lambda_runtime]
  description         = "Common Python dependencies for Lambda functions"

  s3_bucket = local.artefacts_bucket
  s3_key    = "${terraform.workspace}/${var.commit_hash}/${var.gp_search_service_name}-python-dependency-layer-${var.application_tag}.zip"
}
module "lambda" {
  source                = "../../modules/lambda"
  function_name         = "${var.project}-${var.environment}-${var.lambda_name}"
  description           = "GP search Lambda"
  handler               = "functions/gp_search_function.lambda_handler"
  runtime               = var.lambda_runtime
  s3_bucket_name        = local.artefacts_bucket
  s3_key                = "${terraform.workspace}/${var.commit_hash}/${var.gp_search_service_name}-lambda-${var.application_tag}.zip"
  attach_tracing_policy = true
  tracing_mode          = "Active"
  policy_jsons          = [data.aws_iam_policy_document.vpc_access_policy.json]
  timeout               = var.lambda_timeout
  memory_size           = var.lambda_memory_size

  layers = concat(
    [aws_lambda_layer_version.python_dependency_layer.arn],
    var.aws_lambda_layers
  )

  subnet_ids         = [for subnet in data.aws_subnet.private_subnets_details : subnet.id]
  security_group_ids = [aws_security_group.gp_search_lambda_security_group.id]

  environment_variables = {
    "ENVIRONMENT"    = var.environment
    "PROJECT_NAME"   = var.project
    "DB_SECRET_NAME" = var.db_secret_name
    "NAMESPACE"      = "${var.gp_search_service_name}-${local.workspace_suffix}"
  }
}

resource "aws_vpc_security_group_egress_rule" "lambda_allow_egress_to_rds" {
  security_group_id            = aws_security_group.gp_search_lambda_security_group.id
  referenced_security_group_id = data.aws_security_group.rds_security_group.id
  from_port                    = var.rds_port
  ip_protocol                  = "tcp"
  to_port                      = var.rds_port
}

data "aws_iam_policy_document" "vpc_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface"
    ]
    resources = [
      "*"
    ]
  }
}
