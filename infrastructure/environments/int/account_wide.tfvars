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

enable_flow_log           = false
flow_log_s3_force_destroy = true
