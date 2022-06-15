terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.39.0"
    }
  }

  backend "s3" {
    key    = "terraform/pignus-sentry-auth.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = "us-west-2"
}
