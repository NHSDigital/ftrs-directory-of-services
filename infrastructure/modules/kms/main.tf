resource "aws_kms_key" "encryption_key" {
  description             = var.description
  enable_key_rotation     = var.enable_key_rotation
  rotation_period_in_days = var.kms_rotation_period_in_days
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat([
      {
        "Sid" : "SetAccountRootPermissions",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : "arn:aws:iam::${var.account_id}:root"
        },
        "Action" : "kms:*",
        "Resource" : "*"
      },
      {
        "Sid" : "AllowInAccountUseOfKmsKey",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "${var.aws_service_name}"
        },
        "Action" : [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey",
          "kms:ListAliases",
          "kms:ListKeys",
          "kms:CreateGrant",
          "kms:RetireGrant",
          "kms:RevokeGrant"
        ],
        "Resource" : "*",
        "Condition" : {
          "StringEquals" : {
            "aws:SourceAccount" : var.account_id
          }
        }
      }
    ], var.additional_policy_statements)
  })
}

resource "aws_kms_alias" "encryption_key_alias" {
  name          = var.alias_name
  target_key_id = aws_kms_key.encryption_key.key_id
}
