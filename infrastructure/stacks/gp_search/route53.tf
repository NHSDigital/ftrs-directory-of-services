resource "aws_route53_zone" "gp_search_subdomain" {
  name = "servicesearch.${var.environment}.${local.root_domain_name}"
}

data "aws_iam_policy_document" "route53_policy" {
  statement {
    effect = "Allow"
    actions = [
      "CreateHostedZone",
      "route53:ChangeResourceRecordSets",
      "route53:GetChange",
      "route53:ListResourceRecordSets",
      "route53:ListHostedZonesByName",
      "route53:ListHostedZones",
      "route53:GetHostedZone"
    ]
    resources = [
      "arn:aws:route53::${local.account_id}:hostedzone/${aws_route53_zone.gp_search_subdomain.zone_id}"
    ]
  }
}


