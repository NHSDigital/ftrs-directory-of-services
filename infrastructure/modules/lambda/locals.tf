# ==============================================================================
# Context

locals {
  workspace_suffix      = "${terraform.workspace}" == "default" ? "" : "-${terraform.workspace}"
  environment_workspace = "${terraform.workspace}" == "default" ? "" : "${terraform.workspace}"
  common_layers         = ["arn:aws:lambda:eu-west-2:017000801446:layer:AWSLambdaPowertoolsPythonV2:46"]
}
