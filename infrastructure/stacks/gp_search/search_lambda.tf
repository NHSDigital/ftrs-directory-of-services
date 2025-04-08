module "lambda" {
  source                = "../../modules/lambda"
  function_name         = "${var.project}-${var.environment}-${var.lambda_name}"
  description           = "GP search Lambda"
  handler               = "gp_search_function.lambda_handler"
  s3_bucket_name        = local.artefacts_bucket
  s3_key                = "${terraform.workspace}/${var.commit_hash}/${var.service}-lambda-${var.application_tag}.zip"
  attach_policy_jsons   = false
  attach_tracing_policy = true
  tracing_mode          = "Active"
  policy_jsons          = []
  layers                = ["arn:aws:lambda:eu-west-2:017000801446:layer:AWSLambdaPowertoolsPythonV2:46"]

  subnet_ids         = []
  security_group_ids = []
}
