module "opensearch_serverless" {
  source  = "terraform-aws-modules/opensearch/aws//modules/collection"
  version = "1.7.0"

  name             = local.resource_prefix
  description      = "OpenSearch Serverless collection for DynamoDB ingestion"
  type             = var.opensearch_type
  standby_replicas = var.opensearch_standby_replicas

  create_access_policy  = var.opensearch_create_access_policy
  create_network_policy = var.opensearch_create_network_policy

  access_policy = {
    Rules = concat(
      [
        {
          ResourceType = "collection"
          Resource     = ["collection/${local.resource_prefix}"]
          Permission = [
            "aoss:CreateCollectionItems",
            "aoss:UpdateCollectionItems",
            "aoss:DescribeCollectionItems",
            "aoss:DeleteCollectionItems"
          ]
        }
      ],
      [
        for name, tbl in data.aws_dynamodb_table.dynamodb_tables :
        {
          ResourceType = "index"
          Resource     = ["index/${local.resource_prefix}/${tbl.name}"]
          Permission = [
            "aoss:CreateIndex",
            "aoss:UpdateIndex",
            "aoss:DescribeIndex",
            "aoss:DeleteIndex",
            "aoss:ReadDocument",
            "aoss:WriteDocument"
          ]
        }
      ]
    )

    Principal = [
      aws_iam_role.osis_pipelines_role.arn
    ]
  }
}

resource "aws_opensearchserverless_security_policy" "opensearch_serverless_network_access_policy" {
  name        = "${local.resource_prefix}-nap"
  description = "Public access for dashboard, VPC access for collection endpoint"
  type        = "network"

  policy = jsonencode([
    {
      Description     = "Public access for dashboards",
      AllowFromPublic = true
      Rules = [
        {
          Resource     = ["collection/${local.resource_prefix}"]
          ResourceType = "dashboard"
        }
      ]
    },
    {
      Description = "VPC access for collection endpoint",
      Rules = [
        {
          ResourceType = "collection",
          Resource = [
            "collection/${local.resource_prefix}"
          ]
        }
      ],
      AllowFromPublic = false,
      SourceVPCEs = [
        aws_opensearchserverless_vpc_endpoint.vpc_endpoint.id
      ]
    }
  ])
}
