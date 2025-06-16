enable_nat_gateway                     = true
single_nat_gateway                     = false
one_nat_gateway_per_az                 = true
create_database_subnet_group           = true
create_database_route_table            = true
create_database_internet_gateway_route = false
opensearch_type                        = "SEARCH"
opensearch_standby_replicas            = "DISABLED"
opensearch_create_access_policy        = false
opensearch_create_network_policy       = false
opensearch_collection_name             = "-osc"

waf_log_group_policy_name        = "waf-log-group-policy"
osis_apigw_log_group_policy_name = "osis-apigw-log-group-policy"
