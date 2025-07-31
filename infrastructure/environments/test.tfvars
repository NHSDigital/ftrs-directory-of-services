environment         = "test"
data_classification = "3"

vpc = {
  name = "vpc"
  cidr = "10.171.0.0/16"

  public_subnet_a = "10.171.1.0/24"
  public_subnet_b = "10.171.2.0/24"
  public_subnet_c = "10.171.3.0/24"

  private_subnet_a = "10.171.131.0/24"
  private_subnet_b = "10.171.132.0/24"
  private_subnet_c = "10.171.133.0/24"

  database_subnet_a = "10.171.201.0/24"
  database_subnet_b = "10.171.202.0/24"
  database_subnet_c = "10.171.203.0/24"
}

sso_roles = [
  "AWSReservedSSO_DOS-FtRS-RW-Developer_b0ffd523c3b8ddb9",
  "AWSReservedSSO_DOS-FtRS-RW-Infrastructure_e5f5de072b3e7cf8",
]

enable_flow_log           = true
flow_log_s3_force_destroy = true

gp_search_organisation_table_name = "organisation-is"

force_destroy_access_logging_bucket = true
dms_allocated_storage               = 50
