team_owner                        = "data-sourcing"
lambda_runtime                    = "python3.12"
extract_name                      = "extract-lambda"
extract_lambda_handler            = "extract.lambda_handler"
extract_lambda_connection_timeout = 900
extract_lambda_memory_size        = 512

aws_lambda_layers = [
  "arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:16"
]
