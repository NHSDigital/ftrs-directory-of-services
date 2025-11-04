{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DataPipelineReadOnlyAccess",
            "Action": [
                "datapipeline:DescribeObjects",
                "datapipeline:DescribePipelines",
                "datapipeline:GetPipelineDefinition",
                "datapipeline:ListPipelines",
                "datapipeline:QueryObjects"
            ],
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Sid": "KinesisReadOnlyAccess",
            "Action": [
                "kinesis:ListStreams",
                "kinesis:DescribeStream",
                "kinesis:DescribeStreamSummary"
            ],
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Sid": "ResourceGroupsReadOnlyAccess",
            "Effect": "Allow",
            "Action": [
                "resource-groups:ListGroups",
                "resource-groups:ListGroupResources",
                "resource-groups:GetGroup",
                "resource-groups:GetGroupQuery"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DynamoReadOnly",
            "Effect": "Allow",
            "Action": [
                "dynamodb:BatchGetItem",
                "dynamodb:Describe*",
                "dynamodb:List*",
                "dynamodb:GetAbacStatus",
                "dynamodb:GetItem",
                "dynamodb:GetResourcePolicy",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:PartiQLSelect",
                "dax:Describe*",
                "dax:List*",
                "dax:GetItem",
                "dax:BatchGetItem",
                "dax:Query",
                "dax:Scan"
            ],
            "Resource": "*"
        },
        {
            "Sid": "RDSReadOnly",
            "Effect": "Allow",
            "Action": [
                "rds:Describe*",
                "rds:ListTagsForResource"
            ],
            "Resource": "*"
        },
        {
            "Sid": "S3ReadOnly",
            "Effect": "Allow",
            "Action": [
                "s3:Get*",
                "s3:List*",
                "s3:Describe*",
                "s3-object-lambda:Get*",
                "s3-object-lambda:List*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "S3ForAthena",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::${athena_output_bucket_name}/*"
        },
        {
            "Sid": "AthenaLimitedAccess",
            "Effect": "Allow",
            "Action": [
              "athena:Get*",
              "athena:List*",
              "athena:StartQueryExecution",
              "athena:UpdateNamedQuery",
              "athena:StopQueryExecution",
              "athena:CreatePreparedStatement",
              "athena:UpdatePreparedStatement",
              "athena:CreateNamedQuery",
              "athena:CancelQueryExecution",
              "athena:BatchGetNamedQuery"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DMSReadOnlyAccess",
            "Action": [
                "dms:Describe*",
                "dms:List*",
                "dms:TestConnection",
                "dms:DescribeReplicationTasks",
                "dms:DescribeEndpoints"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
