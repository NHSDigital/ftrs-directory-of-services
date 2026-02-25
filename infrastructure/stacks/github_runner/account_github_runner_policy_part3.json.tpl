{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "WAFFullAccess",
            "Effect": "Allow",
            "Action": [
                "waf:*",
                "wafv2:*",
                "waf-regional:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ShieldFullAccess",
            "Effect": "Allow",
            "Action": [
                "shield:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "APIGatewayAccount",
            "Effect": "Allow",
            "Action": [
                "apigateway:*"
            ],
            "Resource": "arn:aws:apigateway:*::/account"
        },
        {
            "Sid": "SecurityHubAccess",
            "Effect": "Allow",
            "Action": [
                "securityhub:GetEnabledStandards",
                "securityhub:BatchDisableStandards",
                "securityhub:BatchEnableStandards"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Inspector2Access",
            "Effect": "Allow",
            "Action": [
                "inspector2:Enable",
                "inspector2:Disable",
                "inspector2:BatchGetAccountStatus",
                "inspector2:GetConfiguration",
                "inspector2:UpdateConfiguration"
            ],
            "Resource": "*"
        },
        {
          "Sid": "FirehoseAccess",
          "Effect": "Allow",
          "Action": [
            "firehose:CreateDeliveryStream",
            "firehose:DeleteDeliveryStream",
            "firehose:DescribeDeliveryStream",
            "firehose:UpdateDestination",
            "firehose:ListDeliveryStreams",
            "firehose:ListTagsForDeliveryStream",
            "firehose:TagDeliveryStream",
            "firehose:StartDeliveryStreamEncryption"
          ],
          "Resource": "*"
        },
        {
          "Sid": "AWSBackupFullAccess",
          "Effect": "Allow",
          "Action": [
            "backup:Create*",
            "backup:Update*",
            "backup:Delete*",
            "backup:Describe*",
            "backup:Get*",
            "backup:List*",
            "backup:Put*",
            "backup:Tag*"
          ],
          "Resource": "*"
        },
        {
          "Sid": "AWSBackupStorageAccess",
          "Effect": "Allow",
          "Action": [
            "backup-storage:*"
          ],
          "Resource": "*"
        }
    ]
}
