data "archive_file" "gp_search_api_lambda_function_archive" {
  type        = "zip"
  source_dir  = "${path.module}/functions/api_function"
  output_path = "${path.module}/functions_zip/${var.gp_search_lambda_name}.zip"
}

module "lambda" {
  source        = "../../modules/lambda"
  filename      = data.archive_file.gp_search_lambda_function_archive.output_path
  function_name = "${var.prefix}-${var.gp_search_lambda_name}"

  tracing_config {
    mode = var.gp_search_lambda_tracing_mode
  }
}
