module "cluster" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "9.10.0"

  name           = var.rds_name
  engine         = var.engine
  engine_version = var.engine_version
  instance_class = var.rds_instance_class
  instances = {
    one = {}
    # 2 = {
    #   instance_class = var.rds_instance_class
    # }
  }

  serverlessv2_scaling_configuration = {
    min_capacity = var.rds_min_capacity
    max_capacity = var.rds_max_capacity
  }

  vpc_id                 = var.vpc_id
  create_db_subnet_group = var.create_subnet_group
  create_security_group  = var.create_security_group
  db_subnet_group_name   = var.rds_db_subnet_group
  vpc_security_group_ids = [aws_security_group.rds_security_group.id]
  master_username        = var.master_username
  master_password        = var.master_password
  skip_final_snapshot    = var.skip_final_snapshot
  security_group_rules = {
    ex1_ingress = {
      cidr_blocks = var.rds_ingress_cidr
    }
  }

  storage_encrypted   = true
  apply_immediately   = true
  monitoring_interval = 10

  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {
    Terraform = "true"
  }
}

resource "aws_security_group" "rds_security_group" {
  name        = "var.rds_db_subnet_group"
  description = "RDS Security Group"

  vpc_id = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "rds_allow_ingress_from_vpn" {
  security_group_id            = aws_security_group.rds_security_group.id
  referenced_security_group_id = var.referenced_security_group_id
  from_port                    = var.rds_port
  ip_protocol                  = var.ip_protocol
  to_port                      = var.rds_port
}
