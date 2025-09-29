# SRT Role with policy that allows SRT access to Shield and WAF Web ACL
data "aws_iam_policy_document" "srt_policy_document" {
  statement {
    sid    = "SRTAssumeAccess"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["drt.shield.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "srt_role" {
  name               = "${var.resource_name}-srt_role"
  assume_role_policy = data.aws_iam_policy_document.srt_policy_document.json
}

resource "aws_iam_role_policy_attachment" "srt_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSShieldDRTAccessPolicy"
  role       = aws_iam_role.srt_role.name
}
