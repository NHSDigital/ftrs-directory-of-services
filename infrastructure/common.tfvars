project          = "ftrs-dos"
project_owner    = "nhs-uec"
service          = "uec-ftrs"
cost_centre      = "P0675"
data_type        = "PCD"
project_type     = "Pilot"
public_facing    = "no"
service_category = "bronze"
team_owner       = "ftrs"

artefacts_bucket_name = "artefacts-bucket"

dynamodb_table_names = [
  "healthcare-service",
  "location",
  "organisation"
]

aws_accounts = [
  "dev",
  "test",
  "prod"
]

api_domain_name = "api.${var.environment}.${var.root_domain_name}"
