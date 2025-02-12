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
      owner               = var.project_owner
      project             = var.project
      environment         = "${var.environment}${local.workspace_suffix}"
      workspace           = terraform.workspace
      terraform-base-path = replace(path.cwd, "/^.*?(${var.repo_name}\\/)/", "$1")
      TagVersion          = var.tag_version
      service             = var.service
      CostCentre          = var.cost_centre
      data_classification = var.data_classification
      DataType            = var.data_type
      ProjectType         = var.project_type
      PublicFacing        = var.public_facing
      ServiceCategory     = var.service_category
      OnOffPattern        = var.on_off_pattern
    }
  }
}
