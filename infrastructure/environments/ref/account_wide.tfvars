vpc = {
  name = "vpc"
  cidr = "10.170.0.0/16"

  public_subnet_a = "10.178.1.0/24"
  public_subnet_b = "10.178.2.0/24"
  public_subnet_c = "10.178.3.0/24"

  private_subnet_a = "10.178.131.0/24"
  private_subnet_b = "10.178.132.0/24"
  private_subnet_c = "10.178.133.0/24"

  database_subnet_a = "10.178.201.0/24"
  database_subnet_b = "10.178.202.0/24"
  database_subnet_c = "10.178.203.0/24"
}

enable_flow_log           = false
flow_log_s3_force_destroy = true

# One NAT Gateway per availability zone
enable_nat_gateway     = true
single_nat_gateway     = false
one_nat_gateway_per_az = true
