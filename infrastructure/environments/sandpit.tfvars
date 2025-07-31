environment         = "sandpit"
data_classification = "3"

vpc = {
  name = "vpc"
  cidr = "10.172.0.0/16"

  public_subnet_a = "10.172.1.0/24"
  public_subnet_b = "10.172.2.0/24"
  public_subnet_c = "10.172.3.0/24"

  private_subnet_a = "10.172.131.0/24"
  private_subnet_b = "10.172.132.0/24"
  private_subnet_c = "10.172.133.0/24"

  database_subnet_a = "10.172.201.0/24"
  database_subnet_b = "10.172.202.0/24"
  database_subnet_c = "10.172.203.0/24"
}

sso_roles = [
  "AWSReservedSSO_DOS-FtRS-RO-Developer_3bc2e6cdda06c2e5",
  "AWSReservedSSO_DOS-FtRS-RO-Infrastructure_622767900be0d98b",
]

enable_flow_log           = false
flow_log_s3_force_destroy = true

force_destroy_access_logging_bucket = true

dms_replication_instance_class = "dms.t3.micro"
dms_engine                     = "aurora-postgresql"
dms_allocated_storage          = 50
migration_type                 = "full-load-and-cdc"
