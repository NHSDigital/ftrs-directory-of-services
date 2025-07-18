module "migration_store_bucket" {
  source      = "../../modules/s3"
  bucket_name = "${local.resource_prefix}-${var.migration_pipeline_store_bucket_name}"
  versioning  = var.s3_versioning
}

resource "aws_s3_bucket_policy" "migration_store_bucket_policy" {
  bucket = module.migration_store_bucket.s3_bucket_id
  policy = data.aws_iam_policy_document.migration_store_bucket_policy_document.json
}

data "aws_iam_policy_document" "migration_store_bucket_policy_document" {
  statement {
    principals {
      type = "AWS"
      identifiers = [
        module.extract_lambda.lambda_role_arn,
        module.transform_lambda.lambda_role_arn,
        module.load_lambda.lambda_role_arn
      ]
    }

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
      "s3:DeleteObject"
    ]

    resources = [
      module.migration_store_bucket.s3_bucket_arn,
      "${module.migration_store_bucket.s3_bucket_arn}/*"
    ]
  }

  statement {
    principals {
      type = "AWS"
      identifiers = concat([
        local.env_sso_roles,
        data.aws_iam_role.app_github_runner_iam_role.arn
      ])
    }

    actions = [
      "s3:*",
    ]

    resources = [
      module.migration_store_bucket.s3_bucket_arn,
      "${module.migration_store_bucket.s3_bucket_arn}/*",
    ]
  }
}

resource "aws_s3_bucket_notification" "lambda_trigger" {
  bucket = module.migration_store_bucket.s3_bucket_id

  lambda_function {
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "extract/"
    filter_suffix       = ".parquet"
    lambda_function_arn = module.transform_lambda.lambda_function_arn
  }

  lambda_function {
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "transform/"
    filter_suffix       = ".parquet"
    lambda_function_arn = module.load_lambda.lambda_function_arn
  }

  depends_on = [module.transform_lambda, module.load_lambda]
}
