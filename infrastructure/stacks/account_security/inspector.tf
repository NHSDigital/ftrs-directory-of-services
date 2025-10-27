# Enable AWS Inspector2 for the account
resource "aws_inspector2_enabler" "inspector" {
  account_ids    = [local.account_id]
  resource_types = ["ECR", "LAMBDA", "LAMBDA_CODE"]
}
