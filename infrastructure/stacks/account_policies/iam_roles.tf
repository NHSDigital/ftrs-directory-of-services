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
  description      = "Service-linked role for AWS Shield Advanced"
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

data "aws_iam_role" "github_account_role" {
  name = "${var.repo_name}-${var.account_github_runner_role_name}"
}

data "aws_iam_policy_document" "trust_github_runner_roles" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = [data.aws_iam_role.github_account_role.arn]
    }

    actions = ["sts:AssumeRole", "sts:TagSession"]
  }
}

resource "aws_iam_role" "steampipe_role" {
  name               = "${var.repo_name}-${var.steampipe_role_name}"
  assume_role_policy = data.aws_iam_policy_document.trust_github_runner_roles.json
}

# Custom policy for Steampipe/Powerpipe with restricted read-only access
# Only grants permissions needed for AWS Well-Architected Framework and Thrifty mods
data "aws_iam_policy_document" "steampipe_restricted_policy_document" {
  # EC2 - For compute, networking, and cost optimization checks
  statement {
    effect = "Allow"
    actions = [
      "ec2:Describe*",
      "ec2:Get*",
      "ec2:List*",
      "ec2:SearchTransitGatewayRoutes",
    ]
    resources = ["*"]
  }

  # RDS - For database reliability and cost checks
  statement {
    effect = "Allow"
    actions = [
      "rds:Describe*",
      "rds:List*",
    ]
    resources = ["*"]
  }

  # S3 - For storage reliability and cost checks
  statement {
    effect = "Allow"
    actions = [
      "s3:Describe*",
      "s3:Get*",
      "s3:List*",
    ]
    resources = ["*"]
  }

  # IAM - For security and identity checks
  statement {
    effect = "Allow"
    actions = [
      "iam:Get*",
      "iam:List*",
      "iam:GenerateCredentialReport",
      "iam:GenerateServiceLastAccessedDetails",
    ]
    resources = ["*"]
  }

  # CloudWatch - For monitoring and operational excellence checks
  statement {
    effect = "Allow"
    actions = [
      "cloudwatch:Describe*",
      "cloudwatch:Get*",
      "cloudwatch:List*",
    ]
    resources = ["*"]
  }

  # CloudTrail - For logging and compliance checks
  statement {
    effect = "Allow"
    actions = [
      "cloudtrail:Describe*",
      "cloudtrail:Get*",
      "cloudtrail:List*",
      "cloudtrail:LookupEvents",
    ]
    resources = ["*"]
  }

  # CloudFormation - For infrastructure checks
  statement {
    effect = "Allow"
    actions = [
      "cloudformation:Describe*",
      "cloudformation:Get*",
      "cloudformation:List*",
      "cloudformation:DetectStackDrift",
      "cloudformation:DetectStackResourceDrift",
    ]
    resources = ["*"]
  }

  # Lambda - For serverless architecture checks
  statement {
    effect = "Allow"
    actions = [
      "lambda:Get*",
      "lambda:List*",
    ]
    resources = ["*"]
  }

  # DynamoDB - For database reliability and cost checks
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:Describe*",
      "dynamodb:List*",
    ]
    resources = ["*"]
  }

  # ELB/ALB/NLB - For networking and reliability checks
  statement {
    effect = "Allow"
    actions = [
      "elasticloadbalancing:Describe*",
    ]
    resources = ["*"]
  }

  # Auto Scaling - For reliability and performance checks
  statement {
    effect = "Allow"
    actions = [
      "autoscaling:Describe*",
    ]
    resources = ["*"]
  }

  # VPC - For networking security checks
  statement {
    effect = "Allow"
    actions = [
      "ec2:DescribeVpcs",
      "ec2:DescribeSubnets",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeNetworkAcls",
      "ec2:DescribeRouteTables",
      "ec2:DescribeVpcEndpoints",
      "ec2:DescribeNatGateways",
      "ec2:DescribeInternetGateways",
    ]
    resources = ["*"]
  }

  # KMS - For encryption checks
  statement {
    effect = "Allow"
    actions = [
      "kms:Describe*",
      "kms:Get*",
      "kms:List*",
    ]
    resources = ["*"]
  }

  # Backup - For backup and recovery checks
  statement {
    effect = "Allow"
    actions = [
      "backup:Describe*",
      "backup:Get*",
      "backup:List*",
    ]
    resources = ["*"]
  }

  # Config - For configuration compliance checks
  statement {
    effect = "Allow"
    actions = [
      "config:Describe*",
      "config:Get*",
      "config:List*",
      "config:SelectResourceConfig",
    ]
    resources = ["*"]
  }

  # SNS - For notification checks
  statement {
    effect = "Allow"
    actions = [
      "sns:Get*",
      "sns:List*",
    ]
    resources = ["*"]
  }

  # SQS - For messaging checks
  statement {
    effect = "Allow"
    actions = [
      "sqs:Get*",
      "sqs:List*",
    ]
    resources = ["*"]
  }

  # ECS/EKS - For container reliability checks
  statement {
    effect = "Allow"
    actions = [
      "ecs:Describe*",
      "ecs:List*",
      "eks:Describe*",
      "eks:List*",
    ]
    resources = ["*"]
  }

  # CloudFront - For content delivery checks
  statement {
    effect = "Allow"
    actions = [
      "cloudfront:Get*",
      "cloudfront:List*",
    ]
    resources = ["*"]
  }

  # API Gateway - For API management checks
  statement {
    effect = "Allow"
    actions = [
      "apigateway:GET",
    ]
    resources = ["*"]
  }

  # Secrets Manager - For secrets management checks
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:Describe*",
      "secretsmanager:Get*",
      "secretsmanager:List*",
    ]
    resources = ["*"]
  }

  # ACM - For certificate checks
  statement {
    effect = "Allow"
    actions = [
      "acm:Describe*",
      "acm:Get*",
      "acm:List*",
    ]
    resources = ["*"]
  }

  # GuardDuty - For security checks
  statement {
    effect = "Allow"
    actions = [
      "guardduty:Get*",
      "guardduty:List*",
    ]
    resources = ["*"]
  }

  # Cost Explorer - For cost optimization (Thrifty mod)
  statement {
    effect = "Allow"
    actions = [
      "ce:Get*",
      "ce:Describe*",
      "ce:List*",
    ]
    resources = ["*"]
  }

  # Cost and Usage Reports - For cost analysis
  statement {
    effect = "Allow"
    actions = [
      "cur:Describe*",
    ]
    resources = ["*"]
  }

  # Trusted Advisor - For best practice checks
  statement {
    effect = "Allow"
    actions = [
      "support:DescribeTrustedAdvisor*",
    ]
    resources = ["*"]
  }

  # Organizations - For account structure checks
  statement {
    effect = "Allow"
    actions = [
      "organizations:Describe*",
      "organizations:List*",
    ]
    resources = ["*"]
  }

  # Resource Groups - For resource tagging checks
  statement {
    effect = "Allow"
    actions = [
      "resource-groups:Get*",
      "resource-groups:List*",
      "tag:Get*",
    ]
    resources = ["*"]
  }

  # SSM - For systems management checks
  statement {
    effect = "Allow"
    actions = [
      "ssm:Describe*",
      "ssm:Get*",
      "ssm:List*",
    ]
    resources = ["*"]
  }

  # EBS - For volume optimization (Thrifty mod)
  statement {
    effect = "Allow"
    actions = [
      "ec2:DescribeVolumes",
      "ec2:DescribeSnapshots",
      "ec2:DescribeVolumeStatus",
    ]
    resources = ["*"]
  }

  # Elasticache - For caching service checks
  statement {
    effect = "Allow"
    actions = [
      "elasticache:Describe*",
      "elasticache:List*",
    ]
    resources = ["*"]
  }

  # Route53 - For DNS checks
  statement {
    effect = "Allow"
    actions = [
      "route53:Get*",
      "route53:List*",
    ]
    resources = ["*"]
  }

  # WAF - For web application firewall checks
  statement {
    effect = "Allow"
    actions = [
      "waf:Get*",
      "waf:List*",
      "wafv2:Get*",
      "wafv2:List*",
      "waf-regional:Get*",
      "waf-regional:List*",
    ]
    resources = ["*"]
  }

  # Shield - For DDoS protection checks
  statement {
    effect = "Allow"
    actions = [
      "shield:Describe*",
      "shield:Get*",
      "shield:List*",
    ]
    resources = ["*"]
  }

  # Logs - For CloudWatch Logs checks
  statement {
    effect = "Allow"
    actions = [
      "logs:Describe*",
      "logs:Get*",
      "logs:List*",
      "logs:FilterLogEvents",
      "logs:TestMetricFilter",
    ]
    resources = ["*"]
  }

  # Glacier - For archival storage cost checks
  statement {
    effect = "Allow"
    actions = [
      "glacier:Describe*",
      "glacier:Get*",
      "glacier:List*",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "steampipe_restricted_policy" {
  name        = "${var.repo_name}-steampipe-restricted-policy"
  description = "Restricted read-only access for Steampipe/Powerpipe AWS Well-Architected Framework and Thrifty mods"
  policy      = data.aws_iam_policy_document.steampipe_restricted_policy_document.json
}

resource "aws_iam_role_policy_attachment" "steampipe_role_policy_attachment" {
  role       = aws_iam_role.steampipe_role.name
  policy_arn = aws_iam_policy.steampipe_restricted_policy.arn
}
