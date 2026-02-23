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
            "backup:ListBackupPlans",
            "backup:CreateBackupPlan",
            "backup:DeleteBackupPlan",
            "backup:DescribeBackupPlan",
            "backup:UpdateBackupPlan",
            "backup:GetBackupPlan",
            "backup:CreateReportPlan",
            "backup:DeleteReportPlan",
            "backup:DescribeReportPlan",
            "backup:UpdateReportPlan",
            "backup:ListReportPlans",
            "backup:TagResource",
            "backup:ListTags",
            "backup:CreateFramework",
            "backup:DeleteFramework",
            "backup:DescribeFramework",
            "backup:ListFrameworks",
            "backup:CreateBackupVault",
            "backup:DeleteBackupVault",
            "backup:DescribeBackupVault",
            "backup:ListBackupVaults",
            "backup:PutBackupVaultAccessPolicy",
            "backup:GetBackupVaultAccessPolicy",
            "backup:CreateBackupSelection",
            "backup:GetBackupSelection",
            "backup:DeleteBackupSelection",
            "backup:CreateRestoreTestingPlan",
            "backup:DeleteRestoreTestingPlan",
            "backup:GetRestoreTestingPlan",
            "backup:ListRestoreTestingPlans",
            "backup:UpdateRestoreTestingPlan"
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
