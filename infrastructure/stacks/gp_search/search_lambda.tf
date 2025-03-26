data "archive_file" "lambda" {
  type        = "zip"
  source_file = "./lambda/functions/search_function.py"
  output_path = "./lambda/functions_zip/search_function.zip"
}
module "lambda" {
  source                 = "../../modules/lambda"
  source_path            = "./lambda/functions/search_function.py"
  function_name          = "${var.project}-${var.gp_search_lambda_name}-${var.environment}"
  description            = "GP search Lambda"
  handler                = "search_function.lambda_handler"
  attach_policy_jsons    = false
  local_existing_package = "./lambda/functions_zip/search_function.zip"
  attach_tracing_policy  = true
  tracing_mode           = "Active"
  policy_jsons           = []
}
