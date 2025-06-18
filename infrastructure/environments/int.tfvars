environment         = "int"
data_classification = "3"

vpc = {
  name = "vpc"
  cidr = "10.173.0.0/16"

  public_subnet_a = "10.173.1.0/24"
  public_subnet_b = "10.173.2.0/24"
  public_subnet_c = "10.173.3.0/24"

  private_subnet_a = "10.173.131.0/24"
  private_subnet_b = "10.173.132.0/24"
  private_subnet_c = "10.173.133.0/24"

  database_subnet_a = "10.173.201.0/24"
  database_subnet_b = "10.173.202.0/24"
  database_subnet_c = "10.173.203.0/24"
}

sso_roles = [
  "AWSReservedSSO_DOS-FtRS-RO-Developer_3bc2e6cdda06c2e5",
  "AWSReservedSSO_DOS-FtRS-RO-Infrastructure_622767900be0d98b",
]

enable_flow_log              = false
flow_logs_s3_expiration_days = 10
