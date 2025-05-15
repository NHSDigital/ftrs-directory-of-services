resource "aws_security_group" "processor_lambda_security_group" {
  name        = "${local.resource_prefix}-${var.processor_name}${local.workspace_suffix}-sg"
  description = "Security group for etl ods processor lambda"
  vpc_id      = data.aws_vpc.vpc.id
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow outbound HTTPS for API access"
  }
}


resource "aws_security_group" "consumer_lambda_security_group" {
  name        = "${local.resource_prefix}-${var.consumer_name}${local.workspace_suffix}-sg"
  description = "Security group for etl ods consumer lambda"

  vpc_id = data.aws_vpc.vpc.id
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow outbound HTTPS for API access"
  }
}
