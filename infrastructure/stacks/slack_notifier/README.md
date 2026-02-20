# Slack Notifier Stack

Centralized Lambda function that receives CloudWatch alarm notifications via SNS and forwards them to Slack.

## What This Stack Does

- Deploys a Lambda function that formats and sends CloudWatch alarms to Slack
- Creates an SNS topic for receiving alarm notifications
- Subscribes the Lambda to the SNS topic
- Runs in VPC with security group allowing HTTPS egress to Slack

## Architecture

```text
CloudWatch Alarms → SNS Topic → Lambda Function → Slack Webhook
```

## Required Variables

```hcl
slack_webhook_alarms_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

## Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `lambda_runtime` | `python3.11` | Lambda runtime version |
| `lambda_timeout` | `30` | Function timeout in seconds |
| `lambda_memory_size` | `128` | Memory allocation in MB |
| `cloudwatch_logs_retention_days` | `7` | Log retention period |
| `enable_xray_tracing` | `true` | Enable X-Ray tracing |
| `allow_slack_webhook_egress` | `0.0.0.0/0` | CIDR for Slack webhook egress |

## Outputs

- `sns_topic_arn` - SNS topic ARN for CloudWatch alarms
- `lambda_function_arn` - Lambda function ARN
- `lambda_function_name` - Lambda function name (used by other stacks)
- `sns_subscription_arn` - SNS subscription ARN

## Usage in Other Stacks

Reference the deployed Lambda function from other stacks:

```hcl
data "aws_lambda_function" "slack_notifier" {
  function_name = "ftrs-dos-{env}-slack-notifier"
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.slack_notifier.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.monitoring.sns_topic_arn
}

resource "aws_sns_topic_subscription" "alarms_to_slack" {
  topic_arn = module.monitoring.sns_topic_arn
  protocol  = "lambda"
  endpoint  = data.aws_lambda_function.slack_notifier.arn
  depends_on = [aws_lambda_permission.allow_sns_invoke]
}
```

## Resources Created

- `aws_lambda_function` - Slack notification handler
- `aws_lambda_layer_version` - Python dependencies
- `aws_sns_topic` - Alarm notification topic
- `aws_sns_topic_policy` - Allows CloudWatch to publish
- `aws_sns_topic_subscription` - Lambda subscription
- `aws_security_group` - VPC security group for Lambda
- `aws_cloudwatch_log_group` - Lambda logs
