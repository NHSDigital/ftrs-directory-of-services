enable_nat_gateway                     = true
single_nat_gateway                     = false
one_nat_gateway_per_az                 = true
create_database_subnet_group           = true
create_database_route_table            = true
create_database_internet_gateway_route = false
create_database_nat_gateway_route      = true
database_dedicated_network_acl         = true
private_dedicated_network_acl          = true
public_dedicated_network_acl           = true

opensearch_type                  = "SEARCH"
opensearch_standby_replicas      = "DISABLED"
opensearch_create_access_policy  = false
opensearch_create_network_policy = false
opensearch_collection_name       = "-osc"

waf_log_group_policy_name        = "waf-log-group-policy"
osis_apigw_log_group_policy_name = "osis-apigw-log-group-policy"

vpc_flow_logs_bucket_name    = "vpc-flow-logs"
subnet_flow_logs_bucket_name = "subnet-flow-logs"
flow_log_destination_type    = "s3"
flow_log_file_format         = "parquet"
flow_log_s3_versioning       = false
enable_flow_log              = false
flow_logs_s3_expiration_days = 10
