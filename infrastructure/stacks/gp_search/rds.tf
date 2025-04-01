module "gp_search_rds" {
  source              = "../../modules/rds"
  main_project        = var.main_project
  vpc_id              = data.aws_vpc.vpc.id
  rds_instance_class  = var.rds_instance_class
  rds_name            = "${var.project}-${var.rds_name}-${var.environment}"
  engine              = var.rds_engine
  engine_version      = var.rds_engine_version
  rds_db_subnet_group = var.rds_db_subnet_group
  rds_ingress_cidr    = var.rds_ingress_cidr
  rds_port            = var.rds_port
}
