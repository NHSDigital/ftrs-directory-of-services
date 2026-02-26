{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ComputeFullAccess",
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "tag:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "LambdaFullAccess",
            "Effect": "Allow",
            "Action": [
                "lambda:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DataFullAccess",
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "dynamodb:*",
                "rds:CreateDBSubnetGroup",
                "rds:DeleteDBSubnetGroup",
                "rds:DescribeDBSubnetGroups",
                "rds:AddTagsToResource",
                "rds:ListTagsForResource"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ManagementFullAccess",
            "Effect": "Allow",
            "Action": [
                "opensearch:*",
                "aoss:*",
                "secretsmanager:*",
                "ssm:*",
                "sns:*",
                "cloudformation:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "MonitoringFullAccess",
            "Effect": "Allow",
            "Action": [
                "cloudwatch:*",
                "logs:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "NetworkingFullAccess",
            "Effect": "Allow",
            "Action": [
                "acm:*",
                "route53:*",
                "route53domains:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "EventsFullAccess",
            "Effect": "Allow",
            "Action": [
                "events:*"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "KMSFullAccess",
            "Effect": "Allow",
            "Action": [
                "kms:CreateKey",
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:DescribeKey",
                "kms:PutKeyPolicy",
                "kms:List*",
                "kms:TagResource",
                "kms:EnableKeyRotation",
                "kms:DisableKeyRotation",
                "kms:GetKeyRotationStatus",
                "kms:GetKeyPolicy",
                "kms:UntagResource",
                "kms:CreateAlias",
                "kms:DeleteAlias",
                "kms:UpdateAlias",
                "kms:ScheduleKeyDeletion",
                "kms:CancelKeyDeletion",
                "kms:UpdateKeyDescription",
                "kms:CreateGrant",
                "kms:ListGrants",
                "kms:RevokeGrant",
                "kms:RetireGrant"
            ],
            "Resource": "*"
        },
        {
            "Sid": "STSGetCallerIdentity",
            "Effect": "Allow",
            "Action": [
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
