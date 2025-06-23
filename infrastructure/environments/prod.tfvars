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

data_migration_rds_min_capacity = 1
data_migration_rds_max_capacity = 1
