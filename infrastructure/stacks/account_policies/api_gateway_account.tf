resource "aws_api_gateway_account" "api_gateway_account" {
  cloudwatch_role_arn = aws_iam_role.cloudwatch_api_gateway_role.arn

  depends_on = [
    aws_iam_role_policy_attachment.api_gateway_cloudwatch_policy_attachment
  ]
}
