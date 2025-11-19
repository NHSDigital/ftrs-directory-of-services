resource "aws_cloudwatch_log_group" "log_group" {
  # checkov:skip=CKV_AWS_158: TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-378
  # checkov:skip=CKV_AWS_338: TODO https://nhsd-jira.digital.nhs.uk/browse/FTRS-378
  name              = "${local.resource_prefix}-log-group${local.workspace_suffix}"
  retention_in_days = var.cloudfront_logs_retention_in_days
  region            = "us-east-1"
}

# Define a source
resource "aws_cloudwatch_log_delivery_source" "delivery_source" {
  region = "us-east-1"

  name         = "${local.resource_prefix}-delivery-source${local.workspace_suffix}"
  log_type     = "ACCESS_LOGS"
  resource_arn = module.read_only_viewer_cloudfront.cloudfront_distribution_arn
}

# Define a destination - ie where the cloudfront logs go and format
resource "aws_cloudwatch_log_delivery_destination" "delivery_destination" {
  region = "us-east-1"

  name          = "${local.resource_prefix}-log-delivery-destination${local.workspace_suffix}"
  output_format = "json"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.log_group.arn
  }
}

# Configure delivery from source to  destination
resource "aws_cloudwatch_log_delivery" "log_delivery" {
  region = "us-east-1"

  delivery_source_name     = aws_cloudwatch_log_delivery_source.delivery_source.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.delivery_destination.arn

  record_fields = var.included_cloudfront_log_fields
}
