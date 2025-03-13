module "lambda" {
  source                = "../../modules/lambda"
  source_path           = "./lambda/functions/search_function"
  function_name         = "${var.project}-${var.gp_search_lambda_name}-${var.environment}"
  description           = "GP search Lambda"
  handler               = "index.lambda_handler"
  attach_policy_jsons   = false
  attach_tracing_policy = true
  policy_jsons          = []
}
