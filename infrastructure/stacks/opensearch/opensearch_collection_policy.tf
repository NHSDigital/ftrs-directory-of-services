resource "aws_opensearchserverless_security_policy" "opensearch_serverless_network_access_policy" {
  name        = "${var.stack_name}-nap${local.workspace_suffix}"
  description = "Public access for dashboard, VPC access for collection endpoint"
  type        = "network"

  policy = jsonencode([
    {
      Description     = "Public access for dashboards",
      AllowFromPublic = true
      Rules = [
        {
          Resource     = ["collection/${data.aws_opensearchserverless_collection.opensearch_serverless_collection.name}"]
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
            "collection/${data.aws_opensearchserverless_collection.opensearch_serverless_collection.name}"
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

resource "aws_opensearchserverless_access_policy" "opensearch_serverless_data_access_policy" {
  name        = "${var.stack_name}-dap${local.workspace_suffix}"
  type        = "data"
  description = "Allow index and collection access"
  policy = jsonencode([
    {
      Rules = concat(
        [
          {
            ResourceType = "collection"
            Resource     = ["collection/${data.aws_opensearchserverless_collection.opensearch_serverless_collection.name}"]
            Permission = [
              "aoss:CreateCollectionItems",
              "aoss:UpdateCollectionItems",
              "aoss:DescribeCollectionItems",
              "aoss:DeleteCollectionItems"
            ]
          }
        ],
        [
          for name in var.dynamodb_table_names_for_opensearch :
          {
            ResourceType = "index"
            Resource     = ["index/${data.aws_opensearchserverless_collection.opensearch_serverless_collection.name}/${name}${local.workspace_suffix}"]
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
      ),
      Principal = [
        data.aws_caller_identity.current.arn,
        aws_iam_role.osis_pipelines_role.arn
      ]
    }
  ])
}
