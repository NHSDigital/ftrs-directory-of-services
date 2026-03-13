data "archive_file" "splunk_hec_transformer" {
  type        = "zip"
  source_file = "${path.module}/../../../application/lambda/splunk-hec-transformer/handler.py"
  output_path = "${path.module}/splunk-hec-transformer.zip"
}

resource "aws_iam_role" "splunk_hec_transformer_role" {
  name = "${local.resource_prefix}-splunk-hec-transformer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "splunk_hec_transformer_basic" {
  role       = aws_iam_role.splunk_hec_transformer_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "splunk_hec_transformer_kms" {
  name = "${local.resource_prefix}-splunk-hec-transformer-kms"
  role = aws_iam_role.splunk_hec_transformer_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "kms:Decrypt",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      Resource = module.lambda_encryption_key.arn
    }]
  })
}

resource "aws_lambda_function" "splunk_hec_transformer" {
  # checkov:skip=CKV_AWS_116: Dead-letter queue not required for a synchronous Firehose transformer
  # checkov:skip=CKV_AWS_117: VPC not required; Firehose invokes this directly
  # checkov:skip=CKV_AWS_50: X-Ray tracing not required for simple passthrough transformer
  # checkov:skip=CKV_AWS_272: Code signing not enforced for internal tooling lambda
  # checkov:skip=CKV_AWS_115: Concurrency limit not required for synchronous Firehose transformer
  function_name    = "${local.resource_prefix}-splunk-hec-transformer"
  role             = aws_iam_role.splunk_hec_transformer_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.splunk_hec_transformer.output_path
  source_code_hash = data.archive_file.splunk_hec_transformer.output_base64sha256
  timeout          = 60
  description      = "Strips whitespace from Firehose records before Splunk Event HEC delivery"
  kms_key_arn      = module.lambda_encryption_key.arn

  environment {
    variables = {
      DEFAULT_SPLUNK_INDEX = var.splunk_default_index
    }
  }
}

resource "aws_lambda_permission" "firehose_invoke_splunk_hec_transformer" {
  statement_id  = "AllowFirehoseInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.splunk_hec_transformer.function_name
  principal     = "firehose.amazonaws.com"
  source_arn    = aws_kinesis_firehose_delivery_stream.splunk.arn
}
