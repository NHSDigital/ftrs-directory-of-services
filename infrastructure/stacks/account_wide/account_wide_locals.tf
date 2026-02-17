# Define interface endpoint services for loop
locals {
  interface_vpc_endpoints = {
    sqs            = "sqs"
    ssm            = "ssm"
    ssmmessages    = "ssmmessages"
    ec2messages    = "ec2messages"
    kms            = "kms"
    secretsmanager = "secretsmanager"
    rds            = "rds"
    appconfig      = "appconfig"
    appconfigdata  = "appconfigdata"
    lambda         = "lambda"
    logs           = "logs"
  }
}
