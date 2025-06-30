variable "aws_region" {
  type    = string
  default = "eu-west-2"
}

data "aws_caller_identity" "current" {}

provider "aws" {
  region = var.aws_region

  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = false

  default_tags {
    tags = {
      Owner              = var.project_owner
      TeamOwner          = var.team_owner
      Project            = var.project
      Environment        = "${var.environment}${local.workspace_suffix}"
      Workspace          = terraform.workspace
      TerraformPath      = replace(path.cwd, "/^.*?(${var.repo_name}\\/)/", "$1")
      Service            = var.service
      CostCentre         = var.cost_centre
      DataClassification = var.data_classification
      DataType           = var.data_type
      ProjectType        = var.project_type
      PublicFacing       = var.public_facing
      ServiceCategory    = var.service_category
    }
  }
}

provider "aws" {
  region = "us-east-1"
  alias  = "us-east-1"

  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = false

  default_tags {
    tags = {
      Owner              = var.project_owner
      TeamOwner          = var.team_owner
      Project            = var.project
      Environment        = "${var.environment}${local.workspace_suffix}"
      Workspace          = terraform.workspace
      TerraformPath      = replace(path.cwd, "/^.*?(${var.repo_name}\\/)/", "$1")
      Service            = var.service
      CostCentre         = var.cost_centre
      DataClassification = var.data_classification
      DataType           = var.data_type
      ProjectType        = var.project_type
      PublicFacing       = var.public_facing
      ServiceCategory    = var.service_category
    }
  }
}

provider "aws" {
  region = "eu-west-2"
  alias  = "mgmt"

  assume_role {
    role_arn = "arn:aws:iam::${var.mgmt_account_id}:role/${local.domain_cross_account_role}"
  }

  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = false

  default_tags {
    tags = {
      Owner              = var.project_owner
      TeamOwner          = var.team_owner
      Project            = var.project
      Environment        = "${var.environment}${local.workspace_suffix}"
      Workspace          = terraform.workspace
      TerraformPath      = replace(path.cwd, "/^.*?(${var.repo_name}\\/)/", "$1")
      Service            = var.service
      CostCentre         = var.cost_centre
      DataClassification = var.data_classification
      DataType           = var.data_type
      ProjectType        = var.project_type
      PublicFacing       = var.public_facing
      ServiceCategory    = var.service_category
    }
  }
}
