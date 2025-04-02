main_project          = "ftrs-directory-of-services"
project               = "ftrs-dos-integrated-search"
gp_search_bucket_name = "gp-search-s3"

migration_pipeline_store_bucket_name = "pipeline-store"
s3_versioning                        = false

rds_name            = "gp-search-rds"
rds_database        = "gp-search-db"
rds_db_subnet_group = "gp-search-subnet-group"
rds_port            = 5432
rds_engine          = "aurora-postgresql"
rds_engine_version  = "16.4"
rds_instance_class  = "db.t3.small"
rds_ingress_cidr    = ["10.20.0.0/20"]
