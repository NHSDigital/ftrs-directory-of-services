resource "aws_route53_zone" "gp_search_subdomain" {
  name = "servicesearch.${var.environment}.${local.root_domain_name}"
}

resource "aws_iam_policy" "route53_policy" {
  name        = "Route53HostedZonePolicy"
  description = "Policy to manage Route 53 Hosted Zone"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "ManageHostedZone",
        Effect = "Allow",
        Action = [
          "route53:ChangeResourceRecordSets",
          "route53:GetHostedZone",
          "route53:ListResourceRecordSets",
          "route53:ListHostedZonesByName"
        ],
        Resource = "arn:aws:route53::${local.account_id}:hostedzone/${aws_route53_zone.gp_search_subdomain.zone_id}"
      }
    ]
  })
}
