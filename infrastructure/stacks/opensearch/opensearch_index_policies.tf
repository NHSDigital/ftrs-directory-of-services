resource "aws_opensearchserverless_access_policy" "opensearch_collection_data_access_policy" {
  count = local.workspace_suffix == "" ? 0 : 1

  name        = "${var.environment}-${var.stack_name}${local.workspace_suffix}-index-dp"
  type        = "data"
  description = "Collection-level data access policy for OpenSearch collection ${local.opensearch_collection_name} (grants collection & index ops)"

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
        },
        {
          ResourceType = "index"
          Resource     = ["index/${data.aws_opensearchserverless_collection.opensearch_serverless_collection.name}/${local.opensearch_index_name}${local.workspace_suffix}"]
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
          aws_iam_role.osis_pipelines_role.arn
        ],
        local.env_sso_roles
      )
    }
  ])
}
