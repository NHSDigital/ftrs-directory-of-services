resource "aws_securityhub_standards_subscription" "cis_aws_foundations_benchmark_1_4_0" {
  standards_arn = "arn:aws:securityhub:${var.aws_region}::standards/cis-aws-foundations-benchmark/v/1.4.0"
}

resource "aws_securityhub_standards_subscription" "cis_aws_foundations_benchmark_3_0_0" {
  standards_arn = "arn:aws:securityhub:${var.aws_region}::standards/cis-aws-foundations-benchmark/v/3.0.0"
}
