// CloudWatch Alarm to monitor CloudFront 5xx error rate
resource "aws_cloudwatch_metric_alarm" "cloudfront_5xx_errors" {
  alarm_name          = "${local.resource_prefix}-cloudfront-5xx-errors${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "5xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = "120"
  statistic           = "Average"
  threshold           = var.cloudfront_5xx_error_threshold
  alarm_description   = "This metric monitors CloudFront 5xx error rate"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DistributionId = module.read_only_viewer_cloudfront.cloudfront_distribution_id
    Region         = "Global"
  }

  provider = aws.us-east-1
}

// Health check that monitors the CloudFront 5xx error rate alarm status
resource "aws_route53_health_check" "cloudfront_5xx_errors" {
  type                    = "CLOUDWATCH_METRIC"
  cloudwatch_alarm_name   = aws_cloudwatch_metric_alarm.cloudfront_5xx_errors.alarm_name
  cloudwatch_alarm_region = var.aws_region_us_east_1

  insufficient_data_health_status = "Healthy"

  tags = {
    Name = "${local.resource_prefix}-cloudfront-5xx-health-check${local.workspace_suffix}"
  }
  provider = aws.us-east-1
}

// CloudWatch Alarm to monitor CloudFront Latency
resource "aws_cloudwatch_metric_alarm" "cloudfront_latency" {
  alarm_name          = "${local.resource_prefix}-cloudfront-latency${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "OriginLatency"
  namespace           = "AWS/CloudFront"
  period              = "120"
  statistic           = "Average"
  threshold           = var.cloudfront_latency_threshold
  alarm_description   = "This metric monitors CloudFront origin latency"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DistributionId = module.read_only_viewer_cloudfront.cloudfront_distribution_id
    Region         = "Global"
  }

  provider = aws.us-east-1
}

// Health check that monitors the CloudFront latency alarm status
resource "aws_route53_health_check" "cloudfront_latency" {
  type                    = "CLOUDWATCH_METRIC"
  cloudwatch_alarm_name   = aws_cloudwatch_metric_alarm.cloudfront_latency.alarm_name
  cloudwatch_alarm_region = var.aws_region_us_east_1

  insufficient_data_health_status = "Healthy"

  tags = {
    Name = "${local.resource_prefix}-cloudfront-latency-health-check${local.workspace_suffix}"
  }
  provider = aws.us-east-1
}

// CloudWatch Alarm to monitor CloudFront 4xx error rate
resource "aws_cloudwatch_metric_alarm" "cloudfront_4xx_errors" {
  alarm_name          = "${local.resource_prefix}-cloudfront-4xx-errors${local.workspace_suffix}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "4xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = "120"
  statistic           = "Average"
  threshold           = var.cloudfront_4xx_error_threshold
  alarm_description   = "This metric monitors CloudFront 4xx error rate"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DistributionId = module.read_only_viewer_cloudfront.cloudfront_distribution_id
    Region         = "Global"
  }

  provider = aws.us-east-1
}

// Health check that monitors the CloudFront 5xx error rate alarm status
resource "aws_route53_health_check" "cloudfront_4xx_errors" {
  type                    = "CLOUDWATCH_METRIC"
  cloudwatch_alarm_name   = aws_cloudwatch_metric_alarm.cloudfront_4xx_errors.alarm_name
  cloudwatch_alarm_region = var.aws_region_us_east_1

  insufficient_data_health_status = "Healthy"

  tags = {
    Name = "${local.resource_prefix}-cloudfront-4xx-health-check${local.workspace_suffix}"
  }
  provider = aws.us-east-1
}
