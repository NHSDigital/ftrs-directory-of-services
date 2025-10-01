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

resource "aws_iam_role" "shield_service_role" {
  name        = "AWSServiceRoleForAWSShield"
  description = "Allows Shield Advanced to automatically respond to DDoS attacks"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "shield.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "shield_service_role_policy_attachment" {
  role       = aws_iam_role.shield_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSShieldServiceRolePolicy"
}
