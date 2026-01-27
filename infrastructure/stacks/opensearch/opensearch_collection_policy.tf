resource "aws_opensearchserverless_security_policy" "opensearch_serverless_network_access_policy" {
  count       = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0
  name        = "${var.environment}-${var.stack_name}-nap"
  description = "Public access for dashboard, VPC access for collection endpoint"
  type        = "network"

  policy = jsonencode([
    {
      Description     = "Public access for dashboards",
      AllowFromPublic = true
      Rules = [
        {
          Resource     = ["collection/${module.opensearch_serverless[0].name}"]
          ResourceType = "dashboard"
        }
      ]
    }
  ])
}

resource "aws_opensearchserverless_access_policy" "opensearch_serverless_data_access_policy" {
  count       = local.stack_enabled == 1 && local.is_primary_environment ? 1 : 0
  name        = "${var.environment}-${var.stack_name}-dap"
  type        = "data"
  description = "Allow index and collection access"
  policy = jsonencode([
    {
      Rules = concat(
        [
          {
            ResourceType = "collection"
            Resource     = ["collection/${module.opensearch_serverless[0].name}"]
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
            Resource     = ["index/${module.opensearch_serverless[0].name}/${name}${local.workspace_suffix}"]
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
          aws_iam_role.osis_pipelines_role[0].arn,
        ],
        local.env_sso_roles
      )
    }
  ])
}

// NOTE: Collection and dashboards are currently public (AllowFromPublic = true) for ease of testing.
// To make the collection private later, create VPCE(s) in the account-wide stack and supply their IDs
// to this stack, then set AllowFromPublic = false and set SourceVPCEs.
// This should be done once a Lambda (or any other compute running inside a VPC) needs to read or write
// indexes in the collection, so that access occurs over PrivateLink instead of the public endpoint.

resource "aws_opensearchserverless_security_policy" "opensearch_serverless_workspace_network_access_policy" {
  count       = local.stack_enabled == 1 && local.workspace_suffix != "" ? 1 : 0
  name        = "${var.environment}-${var.stack_name}${local.workspace_suffix}-nap"
  description = "Workspace-level network access for collection dashboards and collection endpoint"
  type        = "network"

  policy = jsonencode([
    {
      Description     = "Workspace dashboard access"
      AllowFromPublic = true
      Rules = [
        {
          Resource     = ["collection/${data.aws_opensearchserverless_collection.opensearch_serverless_collection[0].name}"]
          ResourceType = "dashboard"
        }
      ]
    },
    {
      Description     = "Workspace network access for collection"
      AllowFromPublic = true
      Rules = [
        {
          Resource     = ["collection/${data.aws_opensearchserverless_collection.opensearch_serverless_collection[0].name}"]
          ResourceType = "collection"
        }
      ]
    }
  ])
}

resource "aws_opensearchserverless_access_policy" "opensearch_serverless_workspace_data_access_policy" {
  count = local.stack_enabled == 1 && local.workspace_suffix != "" ? 1 : 0

  name        = "${var.environment}-${var.stack_name}${local.workspace_suffix}-dap"
  type        = "data"
  description = "Collection-level data access policy for OpenSearch collection ${data.aws_opensearchserverless_collection.opensearch_serverless_collection[0].name} (grants collection & index ops)"

  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "collection"
          Resource     = ["collection/${data.aws_opensearchserverless_collection.opensearch_serverless_collection[0].name}"]
          Permission = [
            "aoss:CreateCollectionItems",
            "aoss:UpdateCollectionItems",
            "aoss:DescribeCollectionItems",
            "aoss:DeleteCollectionItems"
          ]
        },
        {
          ResourceType = "index"
          Resource     = ["index/${data.aws_opensearchserverless_collection.opensearch_serverless_collection[0].name}/${local.opensearch_index_name}"]
          Permission = [
            "aoss:CreateIndex",
            "aoss:UpdateIndex",
            "aoss:DescribeIndex",
            "aoss:DeleteIndex",
            "aoss:ReadDocument",
            "aoss:WriteDocument"
          ]
        }
      ],
      Principal = concat(
        [
          data.aws_caller_identity.current.arn,
          aws_iam_role.osis_pipelines_role[0].arn
        ],
        local.env_sso_roles
      )
    }
  ])
}
