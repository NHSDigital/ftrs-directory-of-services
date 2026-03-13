
resource "aws_cloudwatch_metric_alarm" "etl_batch_completion" {
  alarm_name          = "etl-batch-incomplete-after-15min-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  datapoints_to_alarm = 3
  threshold           = 99

  metric_query {
    id          = "completion_ratio"
    expression  = "((success + permanent_fail + transformer_fail + dlq) / FILL(started, 1)) * 100"
    label       = "Completion Ratio"
    return_data = true
  }

  metric_query {
    id = "started"
    metric {
      metric_name = "ETLBatchStarted"
      namespace   = "FTRS/ETL"
      period      = 900
      stat        = "Sum"
    }
  }

  metric_query {
    id = "success"
    metric {
      metric_name = "ETLMessageSuccess"
      namespace   = "FTRS/ETL"
      period      = 900
      stat        = "Sum"
    }
  }

  metric_query {
    id = "permanent_fail"
    metric {
      metric_name = "ETLMessagePermanentFailure"
      namespace   = "FTRS/ETL"
      period      = 900
      stat        = "Sum"
    }
  }

  metric_query {
    id = "transformer_fail"
    metric {
      metric_name = "ETLTransformerPermanentFailure"
      namespace   = "FTRS/ETL"
      period      = 900
      stat        = "Sum"
    }
  }

  metric_query {
    id = "dlq"
    metric {
      metric_name = "ETLMessageDLQ"
      namespace   = "FTRS/ETL"
      period      = 900
      stat        = "Sum"
    }
  }

  alarm_description  = "ETL batch not completing within 15 minutes"
  alarm_actions      = [data.aws_sns_topic.alerts.arn]
  treat_missing_data = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "etl_failures" {
  alarm_name          = "etl-processing-failures-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  threshold           = 0

  metric_query {
    id          = "total_failures"
    expression  = "permanent + dlq + transformer_fail"
    label       = "Total Failures"
    return_data = true
  }

  metric_query {
    id = "permanent"
    metric {
      metric_name = "ETLMessagePermanentFailure"
      namespace   = "FTRS/ETL"
      period      = 300
      stat        = "Sum"
    }
  }

  metric_query {
    id = "dlq"
    metric {
      metric_name = "ETLMessageDLQ"
      namespace   = "FTRS/ETL"
      period      = 300
      stat        = "Sum"
    }
  }

  metric_query {
    id = "transformer_fail"
    metric {
      metric_name = "ETLTransformerPermanentFailure"
      namespace   = "FTRS/ETL"
      period      = 300
      stat        = "Sum"
    }
  }

  alarm_description  = "ETL pipeline has processing failures"
  alarm_actions      = [data.aws_sns_topic.alerts.arn]
  treat_missing_data = "notBreaching"
}