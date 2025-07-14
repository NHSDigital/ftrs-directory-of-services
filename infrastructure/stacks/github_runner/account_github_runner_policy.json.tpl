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
                "ssm:*"
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
            "Sid": "IAMFullAccess",
            "Effect": "Allow",
            "Action": [
                "iam:List*",
                "iam:Get*",
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:CreateServiceLinkedRole",
                "iam:DeleteServiceLinkedRole",
                "iam:CreatePolicy",
                "iam:DeletePolicy",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:DeleteRolePolicy",
                "iam:CreatePolicyVersion",
                "iam:DeletePolicyVersion",
                "iam:TagRole",
                "iam:UntagRole",
                "iam:TagPolicy",
                "iam:UntagPolicy",
                "iam:TagOpenIDConnectProvider",
                "iam:UpdateOpenIDConnectProviderThumbprint"
            ],
            "Resource": [
                "arn:aws:iam::aws:policy/PowerUserAccess",
                "arn:aws:iam::*:role/${repo_name}-*",
                "arn:aws:iam::*:policy/${repo_name}-*",
                "arn:aws:iam::*:policy/ro_*",
                "arn:aws:iam::*:policy/rw_*"
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
        },
        {
            "Sid": "AllowIAMListPolicies",
            "Effect": "Allow",
            "Action": [
                "iam:ListPolicies"
            ],
            "Resource": "*"
        }
    ]
}
