
module "migration_store_bucket" {
  source      = "../../modules/s3"
  bucket_name = var.migration_pipeline_store_bucket_name
  versioning  = false
}

resource "aws_s3_bucket_policy" "allow_access_from_another_account" {
  bucket = module.migration_store_bucket.id
  policy = data.aws_iam_policy_document.restrict_access_to_ssl.json
}

# data "aws_iam_policy_document" "restrict_access_to_ssl" {
#   statement {
#       "Sid": "PublicReadGetObject",
#       "Effect": "Allow",
#       "Principal": {
#           "AWS": "*"
#       },
#       "Action": "s3:GetObject",
#       "Resource": "arn:aws:s3:::yourbucketnamehere/*"
#   },
#   {
#       "Sid": "PublicReadGetObject",
#       "Effect": "Deny",
#       "Principal": {
#           "AWS": "*"
#       },
#       "Action": "s3:GetObject",
#       "Resource": "arn:aws:s3:::yourbucketnamehere/*",
#       "Condition":{
#           "Bool":
#           { "aws:SecureTransport": false }
#       }
#   }
# }
