terraform {
  required_version = ">= 1.5.0, < 1.7.2"

  backend "local" {
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.5.0"
    }
  }
}
