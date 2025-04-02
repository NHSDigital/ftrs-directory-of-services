resource "random_pet" "rds_username" {
  length    = 2
  separator = "_"
}

resource "random_password" "rds_password" {
  length  = 16
  special = false
  upper   = true
  lower   = true
}

module "gp_search_rds" {
  source                       = "../../modules/rds"
  main_project                 = var.main_project
  vpc_id                       = data.aws_vpc.vpc.id
  rds_instance_class           = var.rds_instance_class
  manage_master_user_password  = false
  master_username              = random_pet.rds_username.id
  master_password              = random_password.rds_password.result
  rds_name                     = "${var.project}-${var.rds_name}-${var.environment}"
  engine                       = var.rds_engine
  engine_version               = var.rds_engine_version
  rds_db_subnet_group          = "${var.main_project}-${var.environment}-database-subnet-group"
  rds_ingress_cidr             = var.rds_ingress_cidr
  rds_port                     = var.rds_port
  referenced_security_group_id = data.aws_security_group.vpn_security_group.id
  ip_protocol                  = data.aws_ec2_client_vpn_endpoint.client_vpn_endpoint.transport_protocol
  create_subnet_group          = false
}
