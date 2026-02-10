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

regional_waf_hostile_country_codes = [
  "BY",
  "CN",
  "HK",
  "IR",
  "MO",
  "RU",
  "SY",
  "KP",
]

enable_s3_kms_encryption = true

enable_firehose_s3_kms_encryption = true
firehose_log_group_name           = "splunk-firehose-logs"
firehose_name                     = "splunk-firehose"
hec_acknowledgment_timeout        = 300
hec_endpoint_type                 = "Raw"
retry_duration                    = 300
s3_backup_mode                    = "FailedEventsOnly"
