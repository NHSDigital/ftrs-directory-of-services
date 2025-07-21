#trivy:ignore:AVD-AWS-0024
module "terraform_lock_dynamodb" {
  source     = "../../modules/dynamodb"
  table_name = var.terraform_lock_table_name

  hash_key = "LockID"
  attributes = [{
    name = "LockID"
    type = "S"
  }]
}
