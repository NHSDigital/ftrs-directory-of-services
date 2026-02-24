{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "IAMListRolesAccess",
            "Effect": "Allow",
            "Action": [
                "iam:ListRoles"
            ],
            "Resource": [
                "arn:aws:iam::*:role/"
            ]
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
                "iam:UntagInstanceProfile",
                "iam:UpdateAssumeRolePolicy",
                "iam:UpdateRoleDescription"
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
                "arn:aws:iam::*:role/aws-service-role/shield.amazonaws.com/AWSServiceRoleForAWSShield",
                "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
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
                        "ec2.amazonaws.com",
                        "drt.shield.amazonaws.com",
                        "lambda.amazonaws.com"
                    ]
                }
            }
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
          "Sid": "AllowServiceLinkedRoleCreation",
          "Effect": "Allow",
          "Action": "iam:CreateServiceLinkedRole",
          "Resource": "*",
          "Condition": {
            "StringEquals": {
                    "iam:AWSServiceName": [
                        "observability.aoss.amazonaws.com",
                        "access-analyzer.amazonaws.com",
                        "agentless.inspector2.amazonaws.com",
                        "inspector2.amazonaws.com",
                        "shield.amazonaws.com"
                    ]
                }
            }
        },
        {
          "Sid": "FirehosePassRole",
          "Effect": "Allow",
          "Action": "iam:PassRole",
          "Resource": "arn:aws:iam::*:role/${repo_name}-*-splunk-firehose-role",
          "Condition": {
            "StringEquals": {
              "iam:PassedToService": "firehose.amazonaws.com"
            }
          }
        },
        {
            "Sid": "AssumeSteamPipeReadOnlyRole",
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole",
                "sts:TagSession"
            ],
            "Resource": "arn:aws:iam::*:role/${repo_name}-steampipe-readonly-role"
        }
    ]
}
