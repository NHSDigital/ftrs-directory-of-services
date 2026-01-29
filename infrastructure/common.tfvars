project          = "ftrs-dos"
project_owner    = "nhs-uec"
service          = "uec-ftrs"
cost_centre      = "P0675"
data_type        = "PCD"
project_type     = "Pilot"
public_facing    = "no"
service_category = "bronze"
team_owner       = "ftrs"

artefacts_bucket_name  = "artefacts-bucket"
s3_logging_bucket_name = "s3-access-logs"

dynamodb_table_names = [
  "healthcare-service",
  "location",
  "organisation",
  "triage-code",
]

root_domain_name = "ftrs.cloud.nhs.uk"

s3_trust_store_bucket_name = "truststore"

organisation_table_name = "organisation"

rds_port = 5432

appconfig_lambda_extension_aws_account_id = "282860088358" # gitleaks:allow
appconfig_lambda_extension_layer_arn      = "arn:aws:lambda:${var.aws_region}:${var.appconfig_lambda_extension_aws_account_id}:layer:AWS-AppConfig-Extension:207"