resource "aws_opensearchserverless_security_policy" "opensearch_serverless_network_access_policy" {
  name        = "${var.environment}-${var.stack_name}-nap${local.workspace_suffix}"
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
    }
  ])
}

resource "aws_opensearchserverless_access_policy" "opensearch_serverless_data_access_policy" {
  for_each = toset(var.dynamodb_table_names_for_opensearch)

  name        = "${var.environment}-${var.stack_name}-dap-${substr(each.key, 0, 3)}${local.workspace_suffix}"
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
          {
            ResourceType = "index"
            Resource     = ["index/${data.aws_opensearchserverless_collection.opensearch_serverless_collection.name}/${each.key}${local.workspace_suffix}"]
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
      Principal = concat(
        [
          data.aws_caller_identity.current.arn,
          aws_iam_role.osis_pipelines_role.arn,
        ],
        local.env_sso_roles
      )
    }
  ])
}
