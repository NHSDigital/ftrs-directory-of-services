module "opensearch_serverless" {
  source  = "terraform-aws-modules/opensearch/aws//modules/collection"
  version = "1.6.0"

  name             = "${var.project}${local.workspace_suffix}"
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
          Resource     = ["collection/${var.project}${local.workspace_suffix}"]
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
          Resource     = ["index/${var.project}${local.workspace_suffix}/${tbl.name}"]
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

resource "aws_opensearchserverless_security_policy" "opensearch_serverless_network_public_dashboard" {
  name        = "${var.project}${local.workspace_suffix}-dashboard"
  description = "Public access for dashboard"
  type        = "network"

  policy = jsonencode([
    {
      AllowFromPublic = true
      Rules = [
        {
          Resource     = ["collection/${var.project}${local.workspace_suffix}"]
          ResourceType = "dashboard"
        }
      ]
    }
  ])
}
