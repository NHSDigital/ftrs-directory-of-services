environment         = "prod"
data_classification = "3"

vpc = {
  name = "vpc"
  cidr = "10.179.0.0/16"

  public_subnet_a = "10.179.1.0/24"
  public_subnet_b = "10.179.2.0/24"
  public_subnet_c = "10.179.3.0/24"

  private_subnet_a = "10.179.131.0/24"
  private_subnet_b = "10.179.132.0/24"
  private_subnet_c = "10.179.133.0/24"

  database_subnet_a = "10.179.201.0/24"
  database_subnet_b = "10.179.202.0/24"
  database_subnet_c = "10.179.203.0/24"
}

sso_roles = [
  "AWSReservedSSO_DOS-FtRS-RO-Infrastructure_49185b4285825a53",
  "AWSReservedSSO_DOS-FtRS-RO-Developer_f86067072e0b2715"
]

enable_flow_log              = true
flow_log_s3_force_destroy    = false
flow_logs_s3_expiration_days = 30

force_destroy_access_logging_bucket = false

dms_instance_multi_az = true
dms_allocated_storage = 50
