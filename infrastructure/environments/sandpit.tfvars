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

data_migration_rds_min_capacity = 1
data_migration_rds_max_capacity = 1
