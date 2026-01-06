resource "aws_opensearchserverless_access_policy" "opensearch_per_index_data_access_policy" {
  count = local.workspace_suffix == "" ? 0 : 1

  name        = "${var.environment}-${var.stack_name}${local.workspace_suffix}"
  type        = "data"
  description = "Per-index access policy for OpenSearch stack ${var.stack_name}${local.workspace_suffix}"

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
            "aoss:WriteDocument"
          ]
        }
      ],
      Principal = concat(
        [
          aws_iam_role.osis_pipelines_role.arn,
          local.github_runner_arn
        ],
        local.env_sso_roles
      )
    }
  ])
}
