resource "aws_opensearchserverless_security_policy" "opensearch_serverless_network_access_policy" {
  count       = local.is_primary_environment ? 1 : 0
  name        = "${var.environment}-${var.stack_name}-nap"
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
  count       = local.is_primary_environment ? 1 : 0
  name        = "${var.environment}-${var.stack_name}-dap"
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

resource "aws_opensearchserverless_security_policy" "opensearch_serverless_workspace_network_access_policy" {
  count       = local.workspace_suffix == "" ? 0 : 1
  name        = "${var.environment}-${var.stack_name}${local.workspace_suffix}-nap"
  description = "Workspace-level network access for collection dashboards and collection endpoint"
  type        = "network"

  policy = jsonencode([
    {
      Description     = "Workspace dashboard access"
      AllowFromPublic = true
      Rules = [
        {
          Resource     = ["collection/${data.aws_opensearchserverless_collection.opensearch_serverless_collection.name}"]
          ResourceType = "dashboard"
        }
      ]
    },
    {
      Description     = "Workspace network access for collection"
      Rules = [
        {
          Resource     = ["collection/${data.aws_opensearchserverless_collection.opensearch_serverless_collection.name}"]
          ResourceType = "collection"
        }
      ]
    }
  ])
}

resource "aws_opensearchserverless_access_policy" "opensearch_serverless_workspace_data_access_policy" {
  count       = local.workspace_suffix == "" ? 0 : 1
  name        = "${var.environment}-${var.stack_name}${local.workspace_suffix}-dap"
  type        = "data"
  description = "Workspace-level data access for collection (allows ingestion by pipeline/runner)"

  policy = jsonencode([
    {
      Rules = [
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
      Principal = concat(
        [
          data.aws_caller_identity.current.arn,
          aws_iam_role.osis_pipelines_role.arn
        ],
        local.env_sso_roles
      )
    }
  ])
}
