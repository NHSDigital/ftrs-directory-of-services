# DoS Search Monitoring Setup

This stack includes CloudWatch monitoring and Slack notifications for Lambda functions.

## Components

### Lambda Alarms (`lambda_alarms.tf`)

- Monitors search Lambda and health check Lambda
- Uses `lambda/comprehensive` template
- Includes Duration, Errors, Throttles, Concurrency, and Invocations alarms
- Exports SNS topic ARN for cross-stack integration

### Slack Notifications (`slack_notifications.tf`)

- Sends CloudWatch alarms to Slack
- Enabled by default (`enable_slack_notifications = true`)
- Uses the `slack_notifier` stack as a module

## Configuration

### Required Variables

Set these in your `terraform.tfvars`:

```hcl
# Slack webhook URL (required if Slack notifications enabled)
slack_webhook_alarms_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Optional Variables

```hcl
# Disable Slack notifications
enable_slack_notifications = false

# Adjust alarm thresholds
search_lambda_duration_p99_critical_ms = 800
search_lambda_errors_critical_threshold = 1
search_lambda_concurrent_executions_critical = 100

# Enable warning level alarms
enable_warning_alarms = true
```

See `terraform.tfvars.example` for all available options.

## Deployment

```bash
# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply
```

## Testing

### Trigger Test Alarm

```bash
aws cloudwatch set-alarm-state \
  --alarm-name "dos-search-search-lambda-errors-critical" \
  --state-value ALARM \
  --state-reason "Testing Slack notifications"
```

### Check Slack Lambda Logs

```bash
aws logs tail /aws/lambda/dos-search-slack-notifier-slack-notification --follow
```

### Verify SNS Subscription

```bash
SNS_ARN=$(terraform output -raw lambda_monitoring_sns_topic_arn)
aws sns list-subscriptions-by-topic --topic-arn "$SNS_ARN"
```

## Outputs

- `lambda_monitoring_sns_topic_arn` - SNS topic ARN for alarm notifications
- `lambda_monitoring_sns_topic_name` - SNS topic name

## Alarm Templates

Currently using `lambda/comprehensive` which includes:

- Duration p95 (warning)
- Duration p99 (critical)
- Concurrent Executions (warning + critical)
- Throttles (critical)
- Invocations spike (critical)
- Errors (warning + critical)

To change template, update `alarm_config_path` in `lambda_alarms.tf`:

- `lambda/minimal` - Basic monitoring (Errors, Throttles)
- `lambda/standard` - Recommended (Duration p99, Errors, Throttles, Concurrency)
- `lambda/comprehensive` - Full monitoring (current)

## Troubleshooting

### Slack Notifications Not Received

1. Check webhook URL is correct
2. Verify Lambda logs for errors
3. Check SNS subscription exists
4. Verify VPC configuration allows outbound HTTPS

### Alarms Not Triggering

1. Check alarm state: `aws cloudwatch describe-alarms`
2. Verify Lambda metrics are being published
3. Review threshold values in `variables.tf`

## Related Documentation

- [Main Monitoring Documentation](../../MONITORING.md)
- [CloudWatch Monitoring Module](../../modules/cloudwatch-monitoring/)
- [Slack Notifications Module](../../modules/slack-notifications/)
- [Slack Notifier Stack](../slack_notifier/)
