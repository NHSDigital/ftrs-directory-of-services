resource "aws_iam_role" "dms_vpc_role" {
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
  role       = aws_iam_role.dms_vpc_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonDMSVPCManagementRole"
}

# Create the service-linked role for Shield Advanced
# This ensures the role exists before we try to use Shield Advanced features
resource "aws_iam_service_linked_role" "shield" {
  aws_service_name = "shield.amazonaws.com"
  description      = "Service-linked role for AWS Shield Advanced for the project"
}

# Role and policy for allowing the REST variant of the API Gateway to write logs to specifically named log groups
# in the account
resource "aws_iam_role" "cloudwatch_api_gateway_role" {
  name               = "${var.project}-api-gateway-cloudwatch"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch_policy_attachment" {
  role       = aws_iam_role.cloudwatch_api_gateway_role.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}
