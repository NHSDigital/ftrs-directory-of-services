resource "aws_cloudwatch_log_group" "log_group" {
  count = local.stack_enabled
  # checkov:skip=CKV_AWS_158: Justification: Using AWS default encryption.
  # checkov:skip=CKV_AWS_338: Justification: Non-production do not require long term log retention.
  name              = "${local.resource_prefix}-log-group${local.workspace_suffix}"
  retention_in_days = var.cloudfront_logs_retention_in_days
  provider          = aws.us-east-1
}

# Define a source
resource "aws_cloudwatch_log_delivery_source" "delivery_source" {
  count        = local.stack_enabled
  name         = "${local.resource_prefix}-log-source${local.workspace_suffix}"
  log_type     = "ACCESS_LOGS"
  resource_arn = module.ui_cloudfront[0].cloudfront_distribution_arn
  provider     = aws.us-east-1
}

# Define a destination - ie where the cloudfront logs go and format
resource "aws_cloudwatch_log_delivery_destination" "delivery_destination" {
  count         = local.stack_enabled
  name          = "${local.resource_prefix}-log-destination${local.workspace_suffix}"
  output_format = "json"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.log_group[0].arn
  }

  provider = aws.us-east-1
}

# Configure delivery from source to  destination
resource "aws_cloudwatch_log_delivery" "log_delivery" {
  count = local.stack_enabled

  delivery_source_name     = aws_cloudwatch_log_delivery_source.delivery_source[0].name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.delivery_destination[0].arn

  record_fields = var.included_cloudfront_log_fields
  provider      = aws.us-east-1
}
