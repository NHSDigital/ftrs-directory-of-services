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

enable_flow_log           = true
flow_log_s3_force_destroy = true
