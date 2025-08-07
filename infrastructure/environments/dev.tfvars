environment         = "dev"
data_classification = "3"

vpc = {
  name = "vpc"
  cidr = "10.170.0.0/16"

  vpn_subnet = "11.170.0.0/22"

  public_subnet_a = "10.170.1.0/24"
  public_subnet_b = "10.170.2.0/24"
  public_subnet_c = "10.170.3.0/24"

  private_subnet_a = "10.170.131.0/24"
  private_subnet_b = "10.170.132.0/24"
  private_subnet_c = "10.170.133.0/24"

  database_subnet_a = "10.170.201.0/24"
  database_subnet_b = "10.170.202.0/24"
  database_subnet_c = "10.170.203.0/24"
}

sso_roles = [
  "AWSReservedSSO_DOS-FtRS-RW-Developer_b0ffd523c3b8ddb9",
  "AWSReservedSSO_DOS-FtRS-RW-Infrastructure_e5f5de072b3e7cf8",
]

enable_flow_log           = false
flow_log_s3_force_destroy = true

gp_search_organisation_table_name = "organisation-is"

force_destroy_access_logging_bucket = true

dms_replication_instance_class = "dms.t3.micro"
dms_engine                     = "aurora-postgresql"
dms_allocated_storage          = 50
full_migration_type            = "full-load"
cdc_migration_type             = "cdc"
