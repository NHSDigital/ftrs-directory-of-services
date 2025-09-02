resource "aws_iam_role" "rds_lambda_invoke_role" {
  count = local.is_primary_environment ? 1 : 0
  name  = "${local.resource_prefix}-${var.rds_event_listener_lambda_name}-invoke-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "rds.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "rds_lambda_invoke_policy" {
  count = local.is_primary_environment ? 1 : 0
  name  = "${local.resource_prefix}-${var.rds_event_listener_lambda_name}-invoke-policy"
  role  = aws_iam_role.rds_lambda_invoke_role[0].id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = "lambda:InvokeFunction",
      Resource = module.rds_event_listener_lambda[0].lambda_function_arn
    }]
  })
}

resource "aws_iam_role" "dms_vpc_role" {
  count = local.is_primary_environment ? 1 : 0

  name        = "dms-vpc-role"
  description = "Allows DMS to manage VPC"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "dms.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "dms_vpc_role_policy_attachment" {
  count = local.is_primary_environment ? 1 : 0

  role       = aws_iam_role.dms_vpc_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonDMSVPCManagementRole"
}
