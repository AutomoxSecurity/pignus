/*
  Pignus-Api
  Backend

*/

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.39.0"
    }
  }

  backend "s3" {
    key    = "terraform/pignus-api.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = "us-west-2"
}

provider "aws" {
  alias  = "east"
  region = "us-east-1"
}

# End File: automox/pignus/terraform/pignus-api/backend.tf
