variable "aws_region" {
  type    = string
  default = "eu-west-2"
}

variable "aws_region_us_east_1" {
  type    = string
  default = "us-east-1"
}

data "aws_caller_identity" "current" {}

provider "aws" {
  region = var.aws_region

  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = false

  default_tags {
    tags = local.default_provider_tags
  }
}

provider "aws" {
  region = var.aws_region_us_east_1
  alias  = "us-east-1"

  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = false

  default_tags {
    tags = local.default_provider_tags
  }
}

provider "aws" {
  region = var.aws_region
  alias  = "mgmt"

  assume_role {
    role_arn = "arn:aws:iam::${var.mgmt_account_id}:role/${local.domain_cross_account_role}"
  }

  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = false

  default_tags {
    tags = local.default_provider_tags
  }
}

provider "aws" {
  region = var.aws_region
  alias  = "backup"

  assume_role {
    role_arn = "arn:aws:iam::${var.mgmt_account_id}:role/${local.backup_cross_account_role}"
  }

  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = false

  default_tags {
    tags = local.default_provider_tags
  }
}
