create_database_subnet_group           = true
create_database_route_table            = true
create_database_internet_gateway_route = false
create_database_nat_gateway_route      = true
database_dedicated_network_acl         = true
private_dedicated_network_acl          = true
public_dedicated_network_acl           = true

waf_log_group_policy_name          = "waf-log-group-policy"
osis_apigw_log_group_policy_name   = "osis-apigw-log-group-policy"
regional_waf_log_group_policy_name = "regional-waf-log-group-policy"

vpc_flow_logs_bucket_name    = "vpc-flow-logs"
subnet_flow_logs_bucket_name = "subnet-flow-logs"
flow_log_destination_type    = "s3"
flow_log_file_format         = "parquet"
flow_log_s3_versioning       = false
flow_logs_s3_expiration_days = 10

# WAF
waf_name            = "frontend-waf-web-acl"
waf_scope           = "CLOUDFRONT"
waf_log_group       = "web-acl-logs"
waf_log_group_class = "STANDARD"

# WAF (regional)
regional_waf_name            = "regional-waf-web-acl"
regional_waf_scope           = "REGIONAL"
regional_waf_log_group       = "regional-web-acl-logs"
regional_waf_log_group_class = "STANDARD"

enable_s3_kms_encryption = true

enable_firehose_s3_kms_encryption = true
firehose_log_group_name           = "splunk-firehose-logs"
hec_acknowledgment_timeout        = 300
retry_duration                    = 300
s3_backup_mode                    = "FailedEventsOnly"

cloudtrail_log_retention_days = 30

apim_apigee_cidrs = [
  "35.197.254.55/32",
  "35.246.55.143/32",
]

# S3 alarms: truststore bucket
truststore_s3_5xx_errors_warning_alarm_threshold           = 1
truststore_s3_5xx_errors_critical_alarm_threshold          = 5
truststore_s3_4xx_errors_warning_alarm_threshold           = 25
truststore_s3_4xx_errors_critical_alarm_threshold          = 50
truststore_s3_5xx_errors_warning_alarm_evaluation_periods  = 1
truststore_s3_5xx_errors_critical_alarm_evaluation_periods = 1
truststore_s3_4xx_errors_warning_alarm_evaluation_periods  = 1
truststore_s3_4xx_errors_critical_alarm_evaluation_periods = 1
truststore_s3_5xx_errors_warning_alarm_period              = 300
truststore_s3_5xx_errors_critical_alarm_period             = 300
truststore_s3_4xx_errors_warning_alarm_period              = 300
truststore_s3_4xx_errors_critical_alarm_period             = 300

# WARNING alarm actions are disabled by default (placeholder alarms only)
enable_warning_alarms = false

# S3 alarms: Terraform state bucket
terraform_state_s3_5xx_errors_warning_alarm_threshold           = 1
terraform_state_s3_5xx_errors_critical_alarm_threshold          = 5
terraform_state_s3_4xx_errors_warning_alarm_threshold           = 25
terraform_state_s3_4xx_errors_critical_alarm_threshold          = 50
terraform_state_s3_5xx_errors_warning_alarm_evaluation_periods  = 1
terraform_state_s3_5xx_errors_critical_alarm_evaluation_periods = 1
terraform_state_s3_4xx_errors_warning_alarm_evaluation_periods  = 1
terraform_state_s3_4xx_errors_critical_alarm_evaluation_periods = 1
terraform_state_s3_5xx_errors_warning_alarm_period              = 300
terraform_state_s3_5xx_errors_critical_alarm_period             = 300
terraform_state_s3_4xx_errors_warning_alarm_period              = 300
terraform_state_s3_4xx_errors_critical_alarm_period             = 300

# VPC Endpoint alarms (shared thresholds applied to all VPC endpoints)
vpce_active_connections_warning_alarm_threshold           = 1
vpce_active_connections_critical_alarm_threshold          = 0
vpce_active_connections_warning_alarm_evaluation_periods  = 1
vpce_active_connections_critical_alarm_evaluation_periods = 1
vpce_active_connections_warning_alarm_period              = 300
vpce_active_connections_critical_alarm_period             = 300
