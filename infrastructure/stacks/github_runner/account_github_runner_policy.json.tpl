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
                "ssm:*",
                "sns:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowOpenSearchServerlessServiceLinkedRoleCreation",
            "Effect": "Allow",
            "Action": "iam:CreateServiceLinkedRole",
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                "iam:AWSServiceName": "observability.aoss.amazonaws.com"
                }
            }
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
                "iam:UpdateRole",
                "iam:DeleteRole",
                "iam:CreateServiceLinkedRole",
                "iam:DeleteServiceLinkedRole",
                "iam:CreatePolicy",
                "iam:DeletePolicy",
                "iam:PutRolePolicy",
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
                "iam:UpdateOpenIDConnectProviderThumbprint",
                "iam:CreateInstanceProfile",
                "iam:DeleteInstanceProfile",
                "iam:AddRoleToInstanceProfile",
                "iam:RemoveRoleFromInstanceProfile",
                "iam:GetInstanceProfile",
                "iam:TagInstanceProfile",
                "iam:UntagInstanceProfile"
            ],
            "Resource": [
                "arn:aws:iam::aws:policy/PowerUserAccess",
                "arn:aws:iam::*:role/${repo_name}-*",
                "arn:aws:iam::*:policy/${repo_name}-*",
                "arn:aws:iam::*:policy/ro_*",
                "arn:aws:iam::*:policy/rw_*",
                "arn:aws:iam::*:instance-profile/${repo_name}-*",
                "arn:aws:iam::*:role/dms-vpc-role",
                "arn:aws:iam::*:role/${project}-*",
                "arn:aws:iam::*:policy/${project}-*",
                "arn:aws:iam::*:role/aws-service-role/shield.amazonaws.com/AWSServiceRoleForAWSShield"
            ]
        },
        {
            "Sid": "IAMAccessAnaylzerFullAccess",
            "Effect": "Allow",
            "Action": [
                "access-analyzer:*"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "IAMPassRoleAccess",
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": [
                "arn:aws:iam::*:role/${project}-*",
                "arn:aws:iam::*:role/${repo_name}-*"
            ],
            "Condition": {
                "StringEquals": {
                    "iam:PassedToService": [
                        "apigateway.amazonaws.com",
                        "ec2.amazonaws.com"
                    ]
                }
            }
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
        },
        {
            "Sid": "AllowIAMListPolicies",
            "Effect": "Allow",
            "Action": [
                "iam:ListPolicies"
            ],
            "Resource": "*"
        },
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
            "Sid": "AllowInspector2ServiceLinkedRoleCreation",
            "Effect": "Allow",
            "Action": "iam:CreateServiceLinkedRole",
            "Resource": "arn:aws:iam::*:role/aws-service-role/inspector2.amazonaws.com/AWSServiceRoleForAmazonInspector2",
            "Condition": {
                "StringEquals": {
                "iam:AWSServiceName": "inspector2.amazonaws.com"
                }
            }
        }
    ]
}
