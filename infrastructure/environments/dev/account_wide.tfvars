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

enable_flow_log           = false
flow_log_s3_force_destroy = true
