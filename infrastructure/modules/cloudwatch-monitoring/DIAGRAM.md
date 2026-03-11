# CloudWatch Monitoring Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         AWS Resources to Monitor                        │
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │   Lambda     │    │ API Gateway  │    │     WAF      │               │
│  │  Functions   │    │              │    │              │               │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘               │
│         │                   │                   │                       │
└─────────┼───────────────────┼───────────────────┼───────────────────────┘
          │                   │                   │
          │ Metrics           │ Metrics           │ Metrics
          ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          CloudWatch Metrics                             │
│                                                                         │
│  • Duration (p95, p99)      • 4XXError              • BlockedRequests   │
│  • Errors                   • 5XXError              • AllowedRequests   │
│  • Throttles                • Latency                                   │
│  • ConcurrentExecutions     • Count                                     │
│  • Invocations                                                          │
└─────────────────────────────────────────────────────────────────────────┘
          │
          │ Evaluated against thresholds
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              CloudWatch Monitoring Module (Terraform)                   │
│                                                                         │
│  Inputs:                                                                │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ • alarm_config_path: "lambda/config"                           │     │
│  │ • monitored_resources: { my_lambda = "function-name" }         │     │
│  │ • alarm_thresholds: { my_lambda = { "errors-critical" = 5 } }  │     │
│  │ • alarm_evaluation_periods: { ... }                            │     │
│  │ • alarm_periods: { ... }                                       │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  Creates:                                                               │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ ✓ CloudWatch Alarms (per resource × alarm type)                │     │
│  │ ✓ SNS Topic (encrypted with KMS)                               │     │
│  │ ✓ Alarm tags (api_path, service, severity)                     │     │
│  └────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
          │
          │ Alarm triggered
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SNS Topic (KMS Encrypted)                            │
│                                                                         │
│  Topic: "my-service-lambda-alarms"                                      │
│  Display: "My Service Lambda Alarms"                                    │
└─────────────────────────────────────────────────────────────────────────┘
          │
          │ Publishes notification
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SNS Topic Subscription                               │
│                                                                         │
│  Protocol: lambda                                                       │
│  Endpoint: slack-notifier Lambda ARN                                    │
└─────────────────────────────────────────────────────────────────────────┘
          │
          │ Invokes
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Slack Notifier Lambda                                │
│                                                                         │
│  Formats alarm details and sends to Slack channel                       │
└─────────────────────────────────────────────────────────────────────────┘
          │
          │ Posts message
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Slack Channel                                   │
│                                                                         │
│  🚨 CRITICAL: my-lambda errors-critical                                 │
│  Threshold: 5 errors exceeded                                           │
│  Service: My Service | API: /my-endpoint                                │
└─────────────────────────────────────────────────────────────────────────┘
```

## Flow Summary

1. **Monitor** - AWS resources emit metrics to CloudWatch
2. **Configure** - Terraform module creates alarms with custom thresholds
3. **Detect** - CloudWatch evaluates metrics against alarm thresholds
4. **Alert** - Triggered alarms publish to SNS topic
5. **Subscribe** - Slack notifier Lambda subscribes to SNS topic
6. **Notify** - Lambda formats and sends alerts to Slack

## Example Alarm Configuration

```text
Resource: my_lambda
├── duration-p95-warning (300ms, 2 periods of 60s)
├── duration-p99-critical (500ms, 2 periods of 60s)
├── errors-warning (3 errors, 2 periods of 60s)
├── errors-critical (5 errors, 2 periods of 60s)
├── throttles-critical (1 throttle, 1 period of 60s)
├── concurrent-executions-warning (80, 2 periods of 60s)
├── concurrent-executions-critical (100, 2 periods of 60s)
└── invocations-spike-critical (1000, 1 period of 300s)
```
