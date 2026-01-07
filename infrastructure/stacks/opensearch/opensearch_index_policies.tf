resource "aws_opensearchserverless_access_policy" "opensearch_index_data_access_policy" {
  count = local.workspace_suffix == "" ? 0 : 1

  name        = "${var.environment}-${var.stack_name}${local.workspace_suffix}-index-dp"
  type        = "data"
  description = "Index-level access policy for OpenSearch stack ${var.stack_name}${local.workspace_suffix} (allows document read/write and index management)"

  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "index"
          Resource     = ["index/${local.opensearch_collection_name}/${local.opensearch_index_name}"]
          Permission = [
            "aoss:CreateIndex",
            "aoss:UpdateIndex",
            "aoss:DescribeIndex",
            "aoss:DeleteIndex",
            "aoss:ReadDocument",
            "aoss:WriteDocument",
            "aoss:DeleteDocument"
          ]
        }
      ],
      Principal = concat(
        [
          aws_iam_role.osis_pipelines_role.arn
        ],
        local.env_sso_roles
      )
    }
  ])
}
