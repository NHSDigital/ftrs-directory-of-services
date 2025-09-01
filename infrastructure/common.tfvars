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

root_domain_name = "ftrs.cloud.nhs.uk"

s3_trust_store_bucket_name = "truststore"

gp_search_organisation_table_name = "organisation"
