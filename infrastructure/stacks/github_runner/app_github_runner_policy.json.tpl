{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ComputeFullAccess",
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "autoscaling:*",
                "lambda:*",
                "tag:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DataFullAccess",
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "kinesis:*",
                "resource-groups:*",
                "dynamodb:*",
                "rds:*",
                "dms:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowRDSServiceLinkedRoleCreation",
            "Effect": "Allow",
            "Action": "iam:CreateServiceLinkedRole",
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                "iam:AWSServiceName": "rds.amazonaws.com"
                }
            }
        },
        {
            "Sid": "ManagementFullAccess",
            "Effect": "Allow",
            "Action": [
                "apigateway:*",
                "execute-api:*",
                "events:*",
                "schemas:*",
                "scheduler:*",
                "pipes:*",
                "ssm:*",
                "es:*",
                "osis:*",
                "opensearch:*",
                "aoss:*",
                "sqs:*",
                "sns:*",
                "secretsmanager:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowOpenSearchServiceLinkedRoleCreation",
            "Effect": "Allow",
            "Action": "iam:CreateServiceLinkedRole",
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                "iam:AWSServiceName": "osis.amazonaws.com"
                }
            }
        },
        {
            "Sid": "MonitoringFullAccess",
            "Effect": "Allow",
            "Action": [
                "application-autoscaling:*",
                "cloudwatch:*",
                "logs:*",
                "oam:*",
                "xray:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "NetworkingFullAccess",
            "Effect": "Allow",
            "Action": [
                "cloudfront:*",
                "cloudfront-keyvaluestore:*"
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
                "iam:UpdateOpenIDConnectProviderThumbprint"
            ],
            "Resource": [
                "arn:aws:iam::*:role/${repo_name}-*",
                "arn:aws:iam::*:role/${project}-*",
                "arn:aws:iam::*:policy/${project}-*",
                "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
            ]
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
            "Sid": "IAMPassRoleLimited",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::*:role/*",
            "Condition": {
                "StringLike": {
                    "iam:PassedToService": [
                        "lambda.amazonaws.com",
                        "events.amazonaws.com",
                        "scheduler.amazonaws.com",
                        "pipes.amazonaws.com",
                        "osis-pipelines.amazonaws.com"
                    ]
                }
            }
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
          "Sid": "AllowRoute53Access",
          "Effect": "Allow",
          "Action": [
            "route53:ListHostedZones",
            "route53:GetHostedZone",
            "route53:GetChange",
            "route53:ChangeResourceRecordSets",
            "route53:ListResourceRecordSets",
            "route53:ListHostedZonesByName",
            "route53:ListTagsForResource",
            "route53:ChangeTagsForResource"
          ],
          "Resource": "*"
        },
        {
          "Sid": "AllowACMAccess",
          "Effect": "Allow",
          "Action": [
            "acm:GetCertificate",
            "acm:ListCertificates",
            "acm:DescribeCertificate",
            "acm:ListTagsForCertificate"
          ],
          "Resource": "*"
        }
    ]
}
